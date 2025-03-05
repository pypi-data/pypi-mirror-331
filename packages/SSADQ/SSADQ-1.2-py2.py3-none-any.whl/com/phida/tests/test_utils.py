import pytest

from com.phida.main.utils import convertToUnixPath, pathExists, convertStrToList, filePathExists
from pyspark.sql.utils import AnalysisException


def test_convert_to_unix_path():
    dbfs_path = "dbfs:/tmp/target/table_path"
    unix_path = convertToUnixPath(dbfs_path)
    assert unix_path == "/dbfs/tmp/target/table_path"


def test_convert_to_unix_path_negative():
    non_dbfs_path = "/tmp/local_path"
    unix_path = convertToUnixPath(non_dbfs_path)
    assert unix_path == "/dbfs" + non_dbfs_path


def test_path_exists_with_existing_path(mocker):
    # Mocking spark.read.load to return successfully
    mocker.patch("pyspark.sql.DataFrameReader.load")

    table_path = "/dbfs/tmp/target/table_path"
    result = pathExists(table_path)

    assert result is True


def test_path_exists_with_non_existing_path(mocker):
    # Mocking spark.read.load to raise AnalysisException
    mocker.patch("pyspark.sql.DataFrameReader.load", side_effect=AnalysisException("Mocked exception"))

    table_path = "/dbfs/non_existent_path"
    result = pathExists(table_path)

    assert result is False


def test_file_path_exists_with_existing_file(mocker):
    # Mocking spark.read.format("csv").load to return successfully
    mocker.patch("pyspark.sql.DataFrameReader.load", return_value="mocked_data")

    file_path = "/dbfs/tmp/target/file_path"
    result = filePathExists(file_path)

    assert result is True


def test_file_path_exists_with_non_existing_file(mocker):
    # Mocking spark.read.format("csv").load to raise AnalysisException
    mocker.patch("pyspark.sql.DataFrameReader.load", side_effect=AnalysisException("Mocked exception"))

    file_path = "/dbfs/non_existent_file"
    result = filePathExists(file_path)

    assert result is False


def test_convert_str_to_list():
    input_string = "abc,efg,hij"
    separator = ","
    result = convertStrToList(input_string, separator)
    expected_result = ["abc", "efg", "hij"]
    assert result == expected_result


def test_convert_str_to_list_with_empty_string():
    # Test case for an empty input string
    input_string = ""
    separator = ","
    result = convertStrToList(input_string, separator)
    expected_result = []
    assert result == expected_result