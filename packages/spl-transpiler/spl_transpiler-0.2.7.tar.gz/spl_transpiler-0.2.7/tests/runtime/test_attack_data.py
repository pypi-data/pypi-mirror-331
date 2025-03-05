import logging
import re
from contextlib import nullcontext, contextmanager
from pathlib import Path
from typing import Annotated

import pandas as pd
import pytest
import yaml
from pydantic import BaseModel, AfterValidator
from pyspark.sql import SparkSession, DataFrame

from spl_transpiler import convert_spl_to_pyspark
from spl_transpiler.macros import substitute_macros
from .utils import data_as_named_table, execute_transpiled_pyspark_code

log = logging.getLogger(__name__)

ATTACK_DATA_ROOT = Path(__file__).parent.parent / "sample_data" / "attack_data"
DATA_DIR = ATTACK_DATA_ROOT / ".data"
INPUTS_DIR = DATA_DIR / "inputs"
OUTPUTS_DIR = DATA_DIR / "outputs"
QUERY_DIR = ATTACK_DATA_ROOT.parent / "queries"


class TestDefinition(BaseModel):
    name: str
    ignore: bool
    input_file: (
        Annotated[Path, AfterValidator(lambda p: INPUTS_DIR / "custom" / p)] | None
    ) = None
    output_file: Annotated[Path, AfterValidator(lambda p: OUTPUTS_DIR / p)]
    query_file: Annotated[Path, AfterValidator(lambda p: QUERY_DIR / p)]

    @contextmanager
    def input_as_main(self, spark):
        context_manager = (
            data_as_named_table(spark, _load_data(self.input_file), "main")
            if self.input_file is not None
            else nullcontext()
        )
        with context_manager:
            yield


class TestSuite(BaseModel):
    # prefix: Annotated[CloudPath, BeforeValidator(cloudpathlib_client.CloudPath)]
    tests: list[TestDefinition]

    @property
    def test_map(self):
        return {test.name: test for test in self.tests}


test_suite_defn = TestSuite.model_validate(
    yaml.safe_load(open(ATTACK_DATA_ROOT / "tests.inputs.yaml"))
)


def _load_data(path: Path) -> DataFrame:
    spark = SparkSession.builder.getOrCreate()
    spark.conf.set("spark.sql.caseSensitive", True)

    assert ".parquet" in path.name, "Let's please just use parquet files for everything"

    return spark.read.parquet(str(path))


@pytest.fixture(scope="session", autouse=True)
def data_models(spark):
    for path in INPUTS_DIR.glob("datamodel/*.parquet"):
        *dm_name, _ = path.name.split(".")
        dm_name = ".".join(dm_name)
        log.info(f"Loading data model from [red]{path.name=} as {dm_name=}")
        df = _load_data(path)
        df.createOrReplaceTempView(f"`{dm_name}`")


@pytest.fixture(scope="session", autouse=True)
def lookups(spark):
    for path in INPUTS_DIR.glob("lookup/*.parquet"):
        dm_name = re.match(r"^([\d\w_]+?)(?:_?\d{8})?\.parquet$", path.name)
        assert dm_name is not None, path.name
        dm_name = dm_name.group(1)
        log.info(f"Loading lookup table from [red]{path.name=} as {dm_name=}")
        df = _load_data(path)
        df.createOrReplaceTempView(f"`{dm_name}`")


def _normalize_df(spark_df: DataFrame):
    df = spark_df.toPandas()

    df = df[list(sorted(df.columns))]
    if "count" in df.columns:
        df["count"] = pd.to_numeric(df["count"], errors="coerce")
    df = df.sort_values(
        by=[
            c
            for c, dtype in sorted(spark_df.dtypes, key=lambda p: p[0])
            if not dtype.startswith("array<")
        ]
    )

    for col, dtype in spark_df.dtypes:
        if dtype.startswith("array<"):
            df[col] = df[col].apply(lambda x: sorted(x) if isinstance(x, list) else x)

    df = df.reset_index(drop=True)

    return df


def _normalize_df_pair(actual, expected):
    expected = expected.replace("null", None)

    for col, dtype in actual.dtypes.items():
        assert col in expected, (
            f"Column {col} found in actual output but missing from expected output"
        )
        try:
            expected[col] = expected[col].astype(dtype)
        except Exception as e:
            raise TypeError(
                f"Column {col} found in both actual and expected outputs, but values in expected output could not be type cast to match actual dtype {dtype}"
            ) from e

    return actual, expected


def _assert_df_equals(actual: DataFrame, expected: DataFrame):
    from pandas.testing import assert_frame_equal

    actual = _normalize_df(actual)
    expected = _normalize_df(expected)

    actual, expected = _normalize_df_pair(actual, expected)

    try:
        assert_frame_equal(actual, expected, check_dtype=False)
    except:
        with pd.option_context("display.max_rows", None, "display.max_columns", None):
            log.error(f"=== Actual ===\n{actual}")
            log.error(f"=== Expected ===\n{expected}")
        raise


@pytest.fixture(scope="session")
def test_results():
    results_path = ATTACK_DATA_ROOT / "tests.outputs.yaml"
    if results_path.exists():
        with open(results_path, "r") as f:
            results = yaml.unsafe_load(f) or {}
    else:
        results = {}

    try:
        yield results
    finally:
        with open(results_path, "w") as f:
            yaml.safe_dump(results, f, sort_keys=False)


# For each sample file, test that the transpiled query, when run against the input data, produces the output data
@pytest.mark.parametrize("test_defn", test_suite_defn.tests, ids=lambda x: x.name)
# @pytest.mark.parametrize("allow_runtime", [True, False], ids=lambda x: "runtime" if x else "standalone")
@pytest.mark.parametrize(
    "allow_runtime", [False], ids=lambda x: "runtime" if x else "standalone"
)
def test_transpiled_query(
    spark, macros, test_defn: TestDefinition, allow_runtime: bool, test_results
) -> None:
    test_results[test_defn.name] = result = dict(
        name=test_defn.name,
        ignore=test_defn.ignore,
        empty=None,
        spl_query=None,
        base_command=None,
        transpiled_query=None,
        success=False,
        error_message=None,
    )

    if test_defn.ignore:
        pytest.skip(f"Skipping test for ignored test {test_defn.name=}")

    try:
        # attack_data = AttackDefinition.load_from_yaml(attack_data_path)
        # If the size of the output_file is 0, skip this test
        output_path = test_defn.output_file
        if not output_path.exists():
            result["empty"] = True
            pytest.skip(f"Skipping test for empty/missing output_file {output_path=}")
        result["empty"] = False

        query = substitute_macros(test_defn.query_file.read_text(), macros)
        result["spl_query"] = query

        _query = query.strip()
        if _query.startswith("|"):
            _query = _query[1:].strip()
            result["base_command"] = _query.split()[0]
        else:
            result["base_command"] = "search"

        log.info(f"Query:\n[green]{query}")
        transpiled_code = convert_spl_to_pyspark(query, allow_runtime=allow_runtime)
        result["transpiled_query"] = transpiled_code

        with test_defn.input_as_main(spark):
            query_results = execute_transpiled_pyspark_code(transpiled_code)
            _assert_df_equals(query_results, _load_data(test_defn.output_file))
            result["success"] = True
    except Exception as e:
        result["error_message"] = str(e)
        raise e
