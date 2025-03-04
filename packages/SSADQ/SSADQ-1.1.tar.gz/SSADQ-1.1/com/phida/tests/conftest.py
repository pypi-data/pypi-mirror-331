import pytest
from pyspark.sql import SparkSession
from pytest_mock import mocker


@pytest.fixture(scope="session")
def spark_session():
    # Create a SparkSession for testing
    spark = SparkSession.builder \
        .appName("pytest-pyspark") \
        .master("local[*]") \
        .getOrCreate()
    yield spark
    # Tear down the SparkSession after testing
    spark.stop()
