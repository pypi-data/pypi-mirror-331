import pytest
import os
import sys

from .utils import data_as_named_table

# Ensures local spark cluster uses same python as is running this test
os.environ["PYSPARK_PYTHON"] = sys.executable


@pytest.fixture(scope="session", autouse=True)
def spark():
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder.appName("Testing PySpark Example")
        .config("spark.driver.memory", "8g")
        .config("spark.executor.memory", "12g")
        .config("spark.sql.session.timeZone", "-00:00")
        .config("spark.sql.caseSensitive", True)
        .master("local[*]")
        .getOrCreate()
    )
    return spark


@pytest.fixture(scope="session", autouse=True)
def sample_data_1(spark):
    return spark.createDataFrame(
        [
            ("src1", "hello world"),
            ("src1", "some text"),
            ("src2", "y=3"),
        ],
        ["_sourcetype", "raw"],
    )


@pytest.fixture(scope="session", autouse=True)
def sample_data_2(spark):
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType

    return spark.createDataFrame(
        [
            ("src1", "hello world", 11),
            ("src1", "some text", 9),
            ("src2", "y=3", None),
        ],
        schema=StructType(
            [
                StructField("_sourcetype", StringType(), True),
                StructField("raw", StringType(), True),
                StructField("maybe_raw_length", IntegerType(), True),
            ]
        ),
    )


@pytest.fixture(scope="session", autouse=True)
def sample_silver_table(spark, sample_data_2):
    with data_as_named_table(spark, sample_data_2, "src1_silver"):
        yield


@pytest.fixture(scope="session", autouse=True)
def sample_model_table(spark, sample_data_2):
    with data_as_named_table(spark, sample_data_2, "Model"):
        yield
