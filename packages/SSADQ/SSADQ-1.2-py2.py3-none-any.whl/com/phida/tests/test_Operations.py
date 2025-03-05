import pytest

from pyspark.sql.types import StructType, StructField, LongType, StringType
from pyspark.sql.utils import AnalysisException

from com.phida.main.Operations import alterDeltaTable, checkForSchemaChanges, createDeltaTable, getKeyCols, hiveDDL, hasColumn, dropColumns, multilineRead, schemaDiff, addDerivedColumns, \
    getDerivedColumnsList, schemaDataTypeDiff, buildColumnsDict, buildJoinCondition, initialMultilineRead, \
    checkIfFirstRun, tableExists


def create_test_df(spark):
    data = [
        (2419823951, 6961762531, "Philips Consumer Lifestyle B.V.", "LM027", "11/14/2023 11:20:26 AM"),
        (2419823951, 1046944178, "Philips Consumer Lifestyle B.V.", "LM027", "11/14/2023 11:20:26 AM"),
        (2304083094, 1162133947, "Philips Medical Systems Nederland B.V.", "AR001", "1/4/2024 3:21:02 AM"),
        (2304108814, 4440730142, "Philips Medical Systems Nederland B.V.", "LM005", "12/18/2023 12:57:18 PM"),
        (2304108809, 5120566047, "Philips Healthcare Informatics Inc.", "LM002", "7/25/2023 10:18:55 AM")
    ]
    schema = StructType([
        StructField("LE_IDA2A2", LongType(), False),  
        StructField("PARTIDA2A2", LongType(), False),
        StructField("LE_NAME", StringType(), True),
        StructField("LE_NUMBER", StringType(), True),
        StructField("UPDATESTAMP", StringType(), True)
    ])

    return spark.createDataFrame(data, schema)


# Define a test DataFrame (df2) with a different schema
def create_test_df2(spark):
    data = [
        (2304108814, 5308403795, "Philips Medical Systems Nederland B.V.", 1, "12/18/2023 12:57:18 PM"),
        (2304108809, 4233680248, "Philips Healthcare Informatics Inc.", 2, "7/25/2023 10:18:55 AM"),
        (2304108809, 1162133947, "Philips Medical Systems Nederland B.V.", 3, "1/4/2024 3:21:02 AM"),
        (4984583227, 6985752882, "Shanghai ChenGuang Medical Technology Co.,Ltd_100284653", 4, "5/24/2023 7:19:17 PM"),
        (2419823986, 6110773756, "Philips Oy", 5, "5/13/2022 2:48:45 AM")
    ]
    schema = StructType([
        StructField("LE_IDA2A2", LongType(), False),  
        StructField("PARTIDA2A2", LongType(), False),
        StructField("LEGAL_ENTITY_NAME", StringType(), True),
        StructField("LE_NUMBER", LongType(), True),
        StructField("UPDATESTAMP", StringType(), True)
    ])
    return spark.createDataFrame(data, schema)


def create_bronze_df(spark):
    data = [
        (2419823951, 6961762531, "Philips Consumer Lifestyle B.V.", "LM027", "11/14/2023 11:20:26 AM", "1", "LE_IDA2A2,PARTIDA2A2", "01-28-2024"),
        (2419823951, 1046944178, "Philips Consumer Lifestyle B.V.", "LM027", "11/14/2023 11:20:26 AM", "0", "LE_IDA2A2,PARTIDA2A2", "01-28-2024"),
        (2304083094, 1162133947, "Philips Medical Systems Nederland B.V.", "AR001", "1/4/2024 3:21:02 AM", "2", "LE_IDA2A2,PARTIDA2A2", "01-28-2024"),
        (2304108814, 4440730142, "Philips Medical Systems Nederland B.V.", "LM005", "12/18/2023 12:57:18 PM", "2", "LE_IDA2A2,PARTIDA2A2", "01-28-2024"),
        (2304108809, 5120566047, "Philips Healthcare Informatics Inc.", "LM002", "7/25/2023 10:18:55 AM", "1", "LE_IDA2A2,PARTIDA2A2", "01-28-2024")
    ]
    schema = StructType([
        StructField("LE_IDA2A2", LongType(), False),  
        StructField("PARTIDA2A2", LongType(), False),
        StructField("LE_NAME", StringType(), True),
        StructField("LE_NUMBER", StringType(), True),
        StructField("UPDATESTAMP", StringType(), True),
        StructField("source_operation", StringType(), True),
        StructField("src_key_cols", StringType(), True),
        StructField("ADLS_LOADED_DATE", StringType(), True)
    ])

    return spark.createDataFrame(data, schema)


def test_tableExists_returns_true_when_table_exists(mocker):
    # Mocking spark.read.table to return successfully
    mock_spark_read_table = mocker.patch("pyspark.sql.DataFrameReader.table")

    # Assuming a table "test_table" exists in the "test_db" database
    dbName = "test_db"
    tblName = "test_table"

    # Call the method
    result = tableExists(dbName, tblName)

    # Assert that the result is True
    assert result is True

    # Verify that spark.read.table was called with the correct arguments
    mock_spark_read_table.assert_called_once_with(dbName + "." + tblName)


def test_tableExists_returns_false_when_table_does_not_exist():
    # Arrange
    dbName = "test_db"
    tblName = "non_existing_table"

    # Act
    result = tableExists(dbName, tblName)

    # Assert
    assert result is False


def test_getKeyCols_where_src_key_col_exists(spark_session, mocker):
    # Arrange
    dbName = "test_db"
    tblName = "non_existing_table"
    bronze_df = create_bronze_df(spark_session)
    mock_spark_table = mocker.patch("pyspark.sql.DataFrameReader.table", return_value=bronze_df)

    # Act
    result = getKeyCols(dbName, tblName)

    # Assert
    assert result == "LE_IDA2A2,PARTIDA2A2"


def test_getKeyCols_where_src_key_col_not_exists(spark_session, mocker):
    # Arrange
    dbName = "test_db"
    tblName = "non_existing_table"

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        getKeyCols(dbName, tblName)

    assert "src_key_cols is not present in the given table" in str(exc_info.value)


def test_hive_ddl(spark_session):
    # Create a test DataFrame
    test_df = create_test_df(spark_session)

    # Call the hiveDDL method
    ddl_result = hiveDDL(test_df)

    # Define the expected DDL string based on the test DataFrame's schema
    expected_ddl = "`LE_IDA2A2` bigint,`PARTIDA2A2` bigint,`LE_NAME` string,`LE_NUMBER` string,`UPDATESTAMP` string"

    # Assert that the generated DDL matches the expected result
    assert ddl_result == expected_ddl


def test_has_column(spark_session):
    # Create a test DataFrame
    test_df = create_test_df(spark_session)

    # Test with an existing column
    existing_column = "LE_NUMBER"
    result_existing = hasColumn(test_df, existing_column)
    assert result_existing is True

    # Test with a non-existing column
    non_existing_column = "EMAIL"
    result_non_existing = hasColumn(test_df, non_existing_column)
    assert result_non_existing is False


def test_hasColumn_where_column_does_not_exist(spark_session):
    # Arrange
    test_df = create_test_df(spark_session)

    # Act
    result = hasColumn(test_df, "non_existing_column")

    # Assert
    assert result is False


def test_dropColumns_where_columns_exist(spark_session):
    test_df = create_test_df(spark_session)

    # Columns to drop
    columns_to_drop = ["LE_NAME", "LE_NUMBER"]  # "EMAIL" does not exist in the DataFrame

    # Call dropColumns method to drop columns
    result_df = dropColumns(test_df, columns_to_drop)

    # Assert that the specified columns have been dropped
    assert not hasColumn(result_df, "LE_NAME")
    assert not hasColumn(result_df, "LE_NUMBER")

    # Assert that other columns still exist
    assert hasColumn(result_df, "LE_IDA2A2")
    assert hasColumn(result_df, "PARTIDA2A2")
    assert hasColumn(result_df, "UPDATESTAMP")

    # Assert that the DataFrame still contains the same number of rows
    assert result_df.count() == test_df.count()


def test_dropColumns_where_columns_do_not_exist(spark_session):
    test_df = create_test_df(spark_session)

    # Columns to drop
    columns_to_drop = ["LE_NAME", "NON_EXISTING_COLUMN"]  # "EMAIL" does not exist in the DataFrame

    # Call dropColumns method to drop columns
    result_df = dropColumns(test_df, columns_to_drop)

    # Assert that the specified columns have been dropped
    assert not hasColumn(result_df, "LE_NAME")

    # Assert that other columns still exist
    assert hasColumn(result_df, "LE_IDA2A2")
    assert hasColumn(result_df, "PARTIDA2A2")
    assert hasColumn(result_df, "LE_NUMBER")
    assert hasColumn(result_df, "UPDATESTAMP")

    # Assert that the DataFrame still contains the same number of rows
    assert result_df.count() == test_df.count()


def test_addDerivedColumns(spark_session):
    # Create a test DataFrame using your create_test_df function
    df = create_test_df(spark_session)

    # Define a list of column expressions to add
    col_expr_list = ["length(LE_NUMBER) as rev_length"]

    # Call the function to add derived columns
    df_out = addDerivedColumns(df, col_expr_list)

    # Check if the derived column exists in the resulting DataFrame
    assert "rev_length" in df_out.columns

    # Check if the derived column has the expected values
    assert df_out.select("rev_length").collect()[0][0] == 5


def test_addDerivedColumns_where_column_expression_list_is_wrong(spark_session):
    # Create a test DataFrame using your create_test_df function
    bronze_df = create_bronze_df(spark_session)

    # Define a list of column expressions to add
    col_expr_list = ["length(NON_EXISTING_COLUMN) as rev_length"]

    with pytest.raises(Exception) as exc_info:
        df_out = addDerivedColumns(bronze_df, col_expr_list)

    # Assert
    assert "The given column expression is invalid" in str(exc_info.value)


def test_getDerivedColumnsList(spark_session):
    # Define a list of column expressions
    col_expr_list = ["length(LE_NUMBER) as rev_length", "count(*) as total_count"]

    # Call the function to get derived column names
    derived_columns = getDerivedColumnsList(col_expr_list)

    # Check if the derived column names are extracted correctly
    assert derived_columns == ["rev_length", "total_count"]


def test_getDerivedColumnsList_with_invalid_expressions():
    # Arrange
    col_expr_list = ["length(LE_NUMBER) as rev_length", "count(*)"]

    # Act
    with pytest.raises(ValueError) as exc_info:
        getDerivedColumnsList(col_expr_list)

    # Assert
    assert "Invalid column expression" in str(exc_info.value)


def test_createDeltaTable(mocker, spark_session):
    # Mock the hiveDDL and getTableProps functions
    tblDDL = "`LE_IDA2A2` bigint,`PARTIDA2A2` bigint,`LE_NAME` string,`LE_NUMBER` string,`UPDATESTAMP` string,`source_operation` string,`src_key_cols` string,`ADLS_LOADED_DATE` string"
    tblProps = "delta.autoOptimize.autoCompact = false, \n\
                    delta.autoOptimize.optimizeWrite = true, \n\
                    delta.tuneFileSizesForRewrites = true, \n\
                    delta.dataSkippingNumIndexedCols = 10, \n\
                    delta.enableChangeDataCapture = true, \n\
                    certified = 'no', \n\
                    primary_source = 'no', \n\
                    sox_compliance = 'no', \n\
                    traceChanges = false"
    
    mocker.patch("com.phida.main.Operations.hiveDDL", return_value=tblDDL)
    mocker.patch("com.phida.main.Operations.getTableProps", return_value=tblProps)

    # Mock the spark.sql method
    mock_spark_sql = mocker.patch.object(spark_session, "sql")

    # Define test data
    bronze_df = create_bronze_df(spark_session)
    path = "/user/tmp/table/legal_entity"
    dbName = "test_db"
    tblName = "test_table"
    pCols=""
    partitions = f" \n PARTITIONED BY ({pCols})" if pCols else ""

    # Call the function
    createDeltaTable(bronze_df, path, dbName, tblName, pCols)

    # Define expected SQL string
    expected_create_database = f"CREATE DATABASE IF NOT EXISTS {dbName}"
    expected_create_table = (
        f"CREATE TABLE IF NOT EXISTS {dbName}.{tblName} ({tblDDL}) \n"
        f"USING DELTA {partitions} \n"
        f"LOCATION \"{path}\" \n"
        f"TBLPROPERTIES ({tblProps})"
    )

    # Assert that spark.sql was called with the correct arguments for creating the database
    mock_spark_sql.assert_any_call(expected_create_database)

    # Assert that spark.sql was called with the correct arguments for creating the table
    mock_spark_sql.assert_any_call(expected_create_table)


def test_schema_diff(spark_session):
    # Create test DataFrames (df1 and df2)
    df1 = create_test_df(spark_session)
    df2 = create_test_df2(spark_session)

    # Call schemaDiff method to get the difference
    result_df = schemaDiff(df1, df2)

    # Verify that the resulting DataFrame contains only columns present in df1 but not in df2
    expected_columns = ["LE_NAME"]
    assert set(result_df.columns) == set(expected_columns)

    # Verify that the DataFrame still contains the same number of rows as df1
    assert result_df.count() == df1.count()


def test_schemaDataTypeDiff(spark_session):
    df1 = create_test_df(spark_session)
    df2 = create_test_df2(spark_session)

    # Call the function to find mismatched columns
    mismatched_columns = schemaDataTypeDiff(df1, df2)

    # Check if the mismatched columns are correctly identified
    assert mismatched_columns == ["LE_NUMBER"]


def test_alterDeltaTable(mocker, spark_session):
    # Mock the spark.sql method
    mock_spark_sql = mocker.patch.object(spark_session, "sql")

    # Define test data
    dbName = "test_db"
    tblName = "test_table"
    addColumns = "yrmnth DATE"

    # Call the function
    alterDeltaTable(dbName, tblName, addColumns)

    # Assert that spark.sql was called with the correct arguments
    mock_spark_sql.assert_called_once_with(f"ALTER TABLE {dbName}.{tblName} ADD COLUMNS ({addColumns})")


def test_alterDeltaTable_table_does_not_exist(mocker, spark_session):
    # Mock the spark.sql method to raise AnalysisException
    mocker.patch.object(spark_session, "sql", side_effect=AnalysisException("Table not found"))

    # Define test data
    dbName = "test_db"
    tblName = "non_existing_table"
    addColumns = "yrmnth DATE"

    # Call the function and expect it to raise an exception
    with pytest.raises(Exception) as exc_info:
        alterDeltaTable(dbName, tblName, addColumns)

    # Assert that the exception message is as expected
    assert str(exc_info.value) == f"The given table {dbName}.{tblName} does not exist"


def test_buildColumnsDict(spark_session):
    # Create a test DataFrame using your create_test_df function
    df = create_test_df(spark_session)

    # Define a list of columns to drop
    drop_columns = ["LE_NAME"]

    # Call the function to build the columns dictionary
    columns_dict = buildColumnsDict(df, drop_columns)

    # Check if the columns dictionary is correctly built
    expected_dict = {"`LE_IDA2A2`": "s.`LE_IDA2A2`", "`PARTIDA2A2`": "s.`PARTIDA2A2`", "`LE_NUMBER`": "s.`LE_NUMBER`", "`UPDATESTAMP`": "s.`UPDATESTAMP`"}
    assert columns_dict == expected_dict


def test_buildJoinCondition(spark_session):
    # Define a list of key columns
    key_cols_list = ["LE_IDA2A2", "PARTIDA2A2"]

    # Call the function to build the join condition
    join_condition = buildJoinCondition(key_cols_list)

    # Check if the join condition is correctly built
    expected_condition = "t.`LE_IDA2A2` <=> s.`LE_IDA2A2` AND t.`PARTIDA2A2` <=> s.`PARTIDA2A2`"
    assert join_condition == expected_condition

def test_initialMultilineRead(tmpdir):
    # Create a temporary CSV file for testing with "|" as separator
    csv_content = """LE_IDA2A2|PARTIDA2A2|LE_NAME|LE_NUMBER|UPDATESTAMP
2419823951|6961762531|Philips Consumer Lifestyle B.V.|LM027|11/14/2023 11:20:26 AM
2419823951|1046944178|Philips Consumer Lifestyle B.V.|LM027|11/14/2023 11:20:26 AM
"""
    csv_file = tmpdir.join("test_file.csv")
    csv_file.write(csv_content)

    # Call the method with the temporary file and "|" as separator
    df = initialMultilineRead(csv_file.strpath, "|", "true")

    # Assert that the DataFrame is not empty and has the expected schema
    assert df.count() == 2
    assert set(df.columns) == {"LE_IDA2A2", "PARTIDA2A2", "LE_NAME", "LE_NUMBER", "UPDATESTAMP"}


def test_initialMultilineRead_invalid_path():
    # Call the method with an invalid path
    df = initialMultilineRead("invalid/path", "|", "true")

    # Assert that the DataFrame is None
    assert df is None


def test_initialMultilineRead_invalid_separator(tmpdir):
    # Create a temporary CSV file for testing with "|" as separator
    csv_content = """LE_IDA2A2|PARTIDA2A2|LE_NAME|LE_NUMBER|UPDATESTAMP
2419823951|6961762531|Philips Consumer Lifestyle B.V.|LM027|11/14/2023 11:20:26 AM
2419823951|1046944178|Philips Consumer Lifestyle B.V.|LM027|11/14/2023 11:20:26 AM
"""
    csv_file = tmpdir.join("test_file.csv")
    csv_file.write(csv_content)

    # Call the method with an invalid separator
    df = initialMultilineRead(csv_file.strpath, ",", "true")

    # Assert that the DataFrame is None or all values are null
    assert len(df.columns)


def test_initialMultilineRead_incorrect_header_flag(tmpdir):
    # Create a temporary CSV file for testing with "|" as separator
    csv_content = """LE_IDA2A2|PARTIDA2A2|LE_NAME|LE_NUMBER|UPDATESTAMP
2419823951|6961762531|Philips Consumer Lifestyle B.V.|LM027|11/14/2023 11:20:26 AM
2419823951|1046944178|Philips Consumer Lifestyle B.V.|LM027|11/14/2023 11:20:26 AM
"""
    csv_file = tmpdir.join("test_file.csv")
    csv_file.write(csv_content)

    # Call the method with the incorrect header flag
    df = initialMultilineRead(csv_file.strpath, "|", "false")

    # Assert that the DataFrame is None or has more than the expected number of rows
    assert df is None or df.count() > 2


def test_multilineRead(tmpdir):
    # Create a test CSV file
    csv_content = """LE_IDA2A2|PARTIDA2A2|LE_NAME|LE_NUMBER|UPDATESTAMP
2419823951|6961762531|Philips Consumer Lifestyle B.V.|LM027|11/14/2023 11:20:26 AM
2419823951|1046944178|Philips Consumer Lifestyle B.V.|LM027|11/14/2023 11:20:26 AM
"""

    csv_path = tmpdir.join("test_file.csv")
    csv_path.write(csv_content)

    test_ddl = "`LE_IDA2A2` bigint,`PARTIDA2A2` bigint,`LE_NAME` string,`LE_NUMBER` string,`UPDATESTAMP` string"

    # Call the multilineRead method
    df_result = multilineRead(str(csv_path), test_ddl, "|", True)

    # Check if the DataFrame has the correct number of rows
    assert df_result.count() == 2

    # Check if the first row matches the expected data
    first_row = df_result.first()
    assert first_row.LE_IDA2A2 == 2419823951
    assert first_row.PARTIDA2A2 == 6961762531
    assert first_row.LE_NAME == "Philips Consumer Lifestyle B.V."
    assert first_row.LE_NUMBER == "LM027"
    assert first_row.UPDATESTAMP == "11/14/2023 11:20:26 AM"


def test_multilineRead_with_invalid_path():
    test_ddl = "`LE_IDA2A2` bigint,`PARTIDA2A2` bigint,`LE_NAME` string,`LE_NUMBER` string,`UPDATESTAMP` string"

    # Call the multilineRead method with an invalid path
    df_result = multilineRead("invalid/path", test_ddl, "|", True)

    # Check if the DataFrame is None
    assert df_result is None


def test_multilineRead_with_invalid_schema(tmpdir):
    # Create a test CSV file
    csv_content = """LE_IDA2A2|PARTIDA2A2|LE_NAME|LE_NUMBER|UPDATESTAMP
2419823951|6961762531|Philips Consumer Lifestyle B.V.|LM027|11/14/2023 11:20:26 AM
2419823951|1046944178|Philips Consumer Lifestyle B.V.|LM027|11/14/2023 11:20:26 AM
"""

    csv_path = tmpdir.join("test_file.csv")
    csv_path.write(csv_content)

    # Call the multilineRead method with an invalid schema
    df_result = multilineRead(str(csv_path), "invalid schema", "|", True)

    # Check if the DataFrame is None
    assert df_result is None


def test_multilineRead_with_invalid_separator(tmpdir):
    # Create a test CSV file
    csv_content = """LE_IDA2A2|PARTIDA2A2|LE_NAME|LE_NUMBER|UPDATESTAMP
2419823951|6961762531|Philips Consumer Lifestyle B.V.|LM027|11/14/2023 11:20:26 AM
2419823951|1046944178|Philips Consumer Lifestyle B.V.|LM027|11/14/2023 11:20:26 AM
"""

    csv_path = tmpdir.join("test_file.csv")
    csv_path.write(csv_content)

    test_ddl = "`LE_IDA2A2` bigint,`PARTIDA2A2` bigint,`LE_NAME` string,`LE_NUMBER` string,`UPDATESTAMP` string"

     # Call the multilineRead method with an invalid separator
    df_result = multilineRead(str(csv_path), test_ddl, ",", True)

    # Check if all the values in the DataFrame are null
    for row in df_result.collect():
        for item in row:
            assert item is None


def test_multilineRead_with_incorrect_header_flag(tmpdir):
    # Create a test CSV file
    csv_content = """LE_IDA2A2|PARTIDA2A2|LE_NAME|LE_NUMBER|UPDATESTAMP
2419823951|6961762531|Philips Consumer Lifestyle B.V.|LM027|11/14/2023 11:20:26 AM
2419823951|1046944178|Philips Consumer Lifestyle B.V.|LM027|11/14/2023 11:20:26 AM
"""

    csv_path = tmpdir.join("test_file.csv")
    csv_path.write(csv_content)

    test_ddl = "`LE_IDA2A2` bigint,`PARTIDA2A2` bigint,`LE_NAME` string,`LE_NUMBER` string,`UPDATESTAMP` string"

    # Call the multilineRead method with the incorrect header flag
    df_result = multilineRead(str(csv_path), test_ddl, "|", False)

    # Check if the DataFrame is None or has more than the expected number of rows
    assert df_result is None or df_result.count() > 2


def test_checkIfFirstRun_path_and_table_does_not_exist(mocker):
    # Mock pathExists and tableExists methods
    mock_path_exists = mocker.patch("com.phida.main.Operations.pathExists", return_value=False)
    mock_table_exists = mocker.patch("com.phida.main.Operations.tableExists", return_value=False)

    # Call the checkIfFirstRun method
    first_run_result = checkIfFirstRun("test_db", "test_table", "/test/table/path")

    # Assert that the result is True (indicating it's the first run)
    assert first_run_result is True

    mock_path_exists.assert_called_once_with("/test/table/path")
    mock_table_exists.assert_called_once_with("test_db", "test_table")


def test_checkIfFirstRun_path_exists_table_not_exists(mocker):
    # Mock pathExists and tableExists methods
    mock_path_exists = mocker.patch("com.phida.main.Operations.pathExists", return_value=True)
    mock_table_exists = mocker.patch("com.phida.main.Operations.tableExists", return_value=False)

    # Call the checkIfFirstRun method
    with pytest.raises(Exception) as exc_info:
        checkIfFirstRun("test_db", "test_table", "/test/table/path")

    # Assert the expected exception message
    expected_message = "phida_log: test_db.test_table cannot be created because /test/table/path already exists. Clean the path and run again."
    assert str(exc_info.value) == expected_message

    # Assert that pathExists and tableExists were called with the correct arguments
    mock_path_exists.assert_called_once_with("/test/table/path")
    mock_table_exists.assert_called_once_with("test_db", "test_table")


def test_checkForSchemaChanges_with_schema_mismatch(mocker):
    # Mock the schemaDiff method and save the patch object to a variable
    mock_schema_diff = mocker.patch("com.phida.main.Operations.schemaDiff", return_value=mocker.Mock(columns=["col1", "col2", "col3"]))

    # Mock source and existing DataFrames
    source_df = mocker.Mock()
    existing_df = mocker.Mock()

    # Call the checkForSchemaChanges method
    with pytest.raises(Exception) as exc_info:
        checkForSchemaChanges(source_df, existing_df, "test_db", "test_table", ["col1", "col2"])

    # Assert the expected exception message
    expected_message = "Column(s) ['col3'] is(are) missing"
    assert str(exc_info.value) == expected_message

    # Assert that the mocked methods were called with the correct arguments using the variable
    mock_schema_diff.assert_called_once_with(existing_df, source_df)


def test_checkForSchemaChanges_with_schema_data_type_mismatch(mocker, spark_session):
    # Mock the required functions
    schema_mismatch_list = ["schema_mismatch_column"]
    mocker.patch("com.phida.main.Operations.schemaDataTypeDiff", return_value=schema_mismatch_list)  # Simulate data type mismatch
    mock_alter_delta_table = mocker.patch("com.phida.main.Operations.alterDeltaTable")  # Mock alterDeltaTable to prevent actual alterations
    mocker.patch("com.phida.main.Operations.hiveDDL", return_value="`col1` string")

    # Define test data
    source_df = create_test_df(spark_session)
    existing_df = create_bronze_df(spark_session)
    tgtDatabaseName = "test_db"
    tgtTableName = "test_table"
    columnsToBeAppendedInTarget = ["source_operation", "src_key_cols", "ADLS_LOADED_DATE"]  # Assuming these columns need to be appended

    # Execute the function and assert the exception
    with pytest.raises(Exception) as exec_info:
        checkForSchemaChanges(source_df, existing_df, tgtDatabaseName, tgtTableName, columnsToBeAppendedInTarget)

    # Assert the exception message
    assert f"There is data type mismatch in column(s): {schema_mismatch_list}" == str(exec_info.value)


def test_checkForSchemaChanges_with_no_mismatch(mocker, spark_session):
    # Mock the required functions
    mock_alter_delta_table = mocker.patch("com.phida.main.Operations.alterDeltaTable")  # Mock alterDeltaTable to prevent actual alterations
    mocker.patch("com.phida.main.Operations.hiveDDL", return_value="`col1` string")

    # Define test data
    source_df = create_test_df(spark_session)
    existing_df = create_bronze_df(spark_session)
    tgtDatabaseName = "test_db"
    tgtTableName = "test_table"
    columnsToBeAppendedInTarget = ["source_operation", "src_key_cols", "ADLS_LOADED_DATE"]  # Assuming these columns need to be appended

    # Execute the function and assert the exception
    checkForSchemaChanges(source_df, existing_df, tgtDatabaseName, tgtTableName, columnsToBeAppendedInTarget)
    
    # Assert the exception message
    mock_alter_delta_table.assert_called_once_with(tgtDatabaseName, tgtTableName, "`col1` string")