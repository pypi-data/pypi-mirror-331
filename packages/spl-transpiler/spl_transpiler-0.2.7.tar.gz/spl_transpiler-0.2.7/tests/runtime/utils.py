import contextlib

from pyspark.sql import DataFrame, functions as F, SparkSession
from rich import print
from rich.syntax import Syntax

from spl_transpiler import convert_spl_to_pyspark
from spl_transpiler.runtime import commands, functions
from spl_transpiler.runtime.utils import exec_with_return


def execute_transpiled_pyspark_code(pyspark_code: str) -> DataFrame:
    global_vars = {
        "spark": SparkSession.builder.getOrCreate(),
        "commands": commands,
        "functions": functions,
        "F": F,
    }
    local_vars = {}

    print(Syntax(pyspark_code, "python"))

    return exec_with_return(pyspark_code, global_vars, local_vars)


def execute_spl_code(spl_code: str) -> DataFrame:
    pyspark_code = convert_spl_to_pyspark(spl_code=spl_code, allow_runtime=True)
    return execute_transpiled_pyspark_code(pyspark_code)


@contextlib.contextmanager
def data_as_named_table(spark: SparkSession, df: DataFrame, name: str):
    try:
        df.cache().createOrReplaceTempView(name)
        yield
    finally:
        spark.catalog.dropTempView(name)
