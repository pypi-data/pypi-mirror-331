from delta import DeltaTable
import pytest
import re

from pyspark.sql.functions import lit, col
from pyspark.sql.types import StructType, StructField, LongType, StringType
from pyspark.sql.window import Window

from com.phida.main.SilverOperations import SilverOperations


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

def create_silver_df(spark):
    data = [
        (2419823952, 6961762533, "Philips Consumer Lifestyle B.V.", "LM027", "11/14/2023 11:20:26 AM", "01-27-2024"),
        (2419823951, 1046944178, "Philips Consumer Lifestyle B.V.", "LM027", "11/14/2023 11:20:26 AM", "01-27-2024"),
        (2304083094, 1162133947, "Philips Medical Systems Nederland B.V.", "AR001", "1/3/2024 3:21:02 AM", "01-27-2024"),
        (2304108814, 4440730142, "Philips Medical Systems Nederland B.V.", "LM005", "12/17/2023 12:57:18 PM", "01-27-2024"),
        (2304108808, 5120566048, "Philips Healthcare Informatics Inc.", "LM002", "7/25/2023 10:18:55 AM", "01-27-2024")
    ]
    schema = StructType([
        StructField("LE_IDA2A2", LongType(), False),  
        StructField("PARTIDA2A2", LongType(), False),
        StructField("LE_NAME", StringType(), True),
        StructField("LE_NUMBER", StringType(), True),
        StructField("UPDATESTAMP", StringType(), True),
        StructField("ADLS_LOADED_DATE", StringType(), True)
    ])

    return spark.createDataFrame(data, schema)


@pytest.fixture
def mocked_silver_operations_with_timestamp(mocker, spark_session):
    
    mocker.patch.object(SilverOperations, "__init__", return_value=None)

    # Create and return a BronzeOperations instance
    silver_operations = SilverOperations()
    silver_operations.srcFilePath = "/path/to/source/file.csv"
    silver_operations.srcDatabaseName = "source_db"
    silver_operations.srcTableName = "source_table"
    silver_operations.tgtDatabaseName = "target_db"
    silver_operations.tgtTableName = "target_table"
    silver_operations.tgtCheckpoint = "/path/to/target/table/checkpoint"
    silver_operations.tgtTablePath = "/path/to/target/table"
    silver_operations.tgtPartitionColumns = ""
    silver_operations.derivedColExpr = ""
    silver_operations.availableNow = "Y"
    silver_operations.dropColumnStr = "source_operation,src_key_cols"
    silver_operations.pruneColumn = ""
    silver_operations.containsTimestamp = True
    silver_operations.srcDF = create_bronze_df(spark_session)
    silver_operations.isDataSourceHVR = False
    silver_operations.keyCols = "LE_IDA2A2,PARTIDA2A2"
    silver_operations.keyColsList = ["LE_IDA2A2", "PARTIDA2A2"]
    silver_operations.joinCondition = "t.`LE_IDA2A2` <=> s.`LE_IDA2A2` AND t.`PARTIDA2A2` <=> s.`PARTIDA2A2`"
    silver_operations.condition = "t.`LE_IDA2A2` <=> s.`LE_IDA2A2` AND t.`PARTIDA2A2` <=> s.`PARTIDA2A2`"
    silver_operations.dropColumnList = ["source_operation", "src_key_cols"]
    silver_operations.columnsDict = {
                                "`LE_IDA2A2`": "s.`LE_IDA2A2`",
                                "`PARTIDA2A2`": "s.`PARTIDA2A2`",
                                "`LE_NAME`": "s.`LE_NAME`",
                                "`LE_NUMBER`": "s.`LE_NUMBER`",
                                "`UPDATESTAMP`": "s.`UPDATESTAMP`",
                                "`ADLS_LOADED_DATE`": "s.`ADLS_LOADED_DATE`"
                            }

    return silver_operations


@pytest.fixture
def mocked_silver_operations_without_timestamp(mocker):

    mocker.patch.object(SilverOperations, "__init__", return_value=None)

    silver_operations = SilverOperations()
    silver_operations.srcFilePath = "/path/to/source/file.csv"
    silver_operations.srcDatabaseName = "source_db"
    silver_operations.srcTableName = "source_table"
    silver_operations.tgtDatabaseName = "target_db"
    silver_operations.tgtTableName = "target_table"
    silver_operations.tgtCheckpoint = "/path/to/target/table/checkpoint"
    silver_operations.tgtTablePath = "/path/to/target/table"
    silver_operations.tgtPartitionColumns = ""
    silver_operations.derivedColExpr = ""
    silver_operations.availableNow = "Y"
    silver_operations.dropColumnStr = "source_operation,src_key_cols"
    silver_operations.pruneColumn = ""
    silver_operations.containsTimestamp = False
    silver_operations.currentDate = "01-28-2024"
    
    return silver_operations

class TestSilverOperations:

    def test_silverCleansing_without_derived_columns(self, mocked_silver_operations_with_timestamp, mocker):

        silver_operations = mocked_silver_operations_with_timestamp

        # Arrange
        mock_table_exists = mocker.patch("com.phida.main.SilverOperations.tableExists", return_value=True)
        mock_add_derived_columns = mocker.patch("com.phida.main.SilverOperations.addDerivedColumns", side_effect=None)
        mock_build_columns_dict = mocker.patch("com.phida.main.SilverOperations.buildColumnsDict", return_value=silver_operations.columnsDict)

        # Act
        result_df = silver_operations.silverCleansing()

        # Assert
        assert result_df.count() == silver_operations.srcDF.count()
        mock_add_derived_columns.assert_not_called()

    
    def test_silverCleansing_with_derived_columns(self, mocked_silver_operations_with_timestamp, mocker):

        silver_operations = mocked_silver_operations_with_timestamp
        silver_operations.derivedColExpr = "cast(LE_IDA2A2 as int) as LE_IDA2A2_INT"

        columns_dict_after_derived = {
                                "`LE_IDA2A2`": "s.`LE_IDA2A2`",
                                "`PARTIDA2A2`": "s.`PARTIDA2A2`",
                                "`LE_NAME`": "s.`LE_NAME`",
                                "`LE_NUMBER`": "s.`LE_NUMBER`",
                                "`UPDATESTAMP`": "s.`UPDATESTAMP`",
                                "`ADLS_LOADED_DATE`": "s.`ADLS_LOADED_DATE`",
                                "`LE_IDA2A2_INT`": "s.`LE_IDA2A2_INT`"
                            }

        # Arrange
        mock_table_exists = mocker.patch("com.phida.main.SilverOperations.tableExists", return_value=True)
        mock_convert_str_to_list = mocker.patch("com.phida.main.SilverOperations.convertStrToList", return_value=["cast(LE_IDA2A2 as int) as LE_IDA2A2_INT"])
        mock_build_columns_dict = mocker.patch("com.phida.main.SilverOperations.buildColumnsDict", return_value=columns_dict_after_derived)    

        # Act
        result_df = silver_operations.silverCleansing()

        # Assert
        assert "LE_IDA2A2_INT" in result_df.columns
        assert result_df.count() == silver_operations.srcDF.count()

    
    def test_prepareTarget_first_run(self, mocked_silver_operations_with_timestamp, mocker, spark_session):
        silver_operations = mocked_silver_operations_with_timestamp

        inDF = create_bronze_df(spark_session)

        # Arrange
        mock_table_exists = mocker.patch("com.phida.main.SilverOperations.tableExists", return_value=False)
        mock_path_exists = mocker.patch("com.phida.main.SilverOperations.pathExists", return_value=False)
        mock_create_delta_table = mocker.patch("com.phida.main.SilverOperations.createDeltaTable") 
        mock_drop_columns = mocker.patch("com.phida.main.SilverOperations.dropColumns", return_value=inDF)

        # Act
        result = silver_operations.prepareTarget(inDF)

        # Assert
        mock_create_delta_table.assert_called_once_with(
            inDF, silver_operations.tgtTablePath, silver_operations.tgtDatabaseName,
            silver_operations.tgtTableName, ""
        )


    def test_prepareTarget_with_schema_diff(self, mocked_silver_operations_with_timestamp, mocker, spark_session):
        silver_operations = mocked_silver_operations_with_timestamp

        inDF = create_bronze_df(spark_session)
        existing_df = create_silver_df(spark_session)
        existing_df = existing_df.withColumn("EXTRA_COLUMN", lit("test"))

        # Arrange
        mock_table_exists = mocker.patch("com.phida.main.SilverOperations.tableExists", return_value=True)
        mock_path_exists = mocker.patch("com.phida.main.SilverOperations.pathExists", return_value=True) 
        mock_drop_columns = mocker.patch("com.phida.main.SilverOperations.dropColumns", return_value=inDF)
        mock_existing_df = mocker.patch("pyspark.sql.DataFrameReader.table", return_value=existing_df)

        with pytest.raises(Exception, match="Column\\(s\\) \\['EXTRA_COLUMN'\\] is\\(are\\) missing"):
            silver_operations.prepareTarget(inDF)

    
    def test_prepareTarget_with_schema_data_type_diff(self, mocked_silver_operations_with_timestamp, mocker, spark_session):
        silver_operations = mocked_silver_operations_with_timestamp

        inDF = create_bronze_df(spark_session)
        existing_df = create_silver_df(spark_session)
        existing_df = existing_df.withColumn("LE_NUMBER", col("LE_NUMBER").cast("int"))

        # Arrange
        mock_table_exists = mocker.patch("com.phida.main.SilverOperations.tableExists", return_value=True)
        mock_path_exists = mocker.patch("com.phida.main.SilverOperations.pathExists", return_value=True) 
        mock_drop_columns = mocker.patch("com.phida.main.SilverOperations.dropColumns", return_value=inDF)
        mock_existing_df = mocker.patch("pyspark.sql.DataFrameReader.table", return_value=existing_df)

        with pytest.raises(Exception, match=re.escape("There is data type mismatch in column(s): ['LE_NUMBER']")):
            silver_operations.prepareTarget(inDF)


    def test_prepareTarget_with_add_columns(self, mocked_silver_operations_with_timestamp, mocker, spark_session):
        silver_operations = mocked_silver_operations_with_timestamp

        inDF = create_bronze_df(spark_session)
        existing_df = create_silver_df(spark_session)

        # Arrange
        mock_table_exists = mocker.patch("com.phida.main.SilverOperations.tableExists", return_value=True)
        mock_path_exists = mocker.patch("com.phida.main.SilverOperations.pathExists", return_value=True) 
        mock_drop_columns = mocker.patch("com.phida.main.SilverOperations.dropColumns", return_value=inDF)
        mock_existing_df = mocker.patch("pyspark.sql.DataFrameReader.table", return_value=existing_df)
        mock_schema_data_type_diff = mocker.patch("com.phida.main.SilverOperations.schemaDataTypeDiff", return_value=[])
        mock_hive_ddl = mocker.patch("com.phida.main.SilverOperations.hiveDDL", return_value="`col1` INT")
        mock_alter_delta_table = mocker.patch("com.phida.main.SilverOperations.alterDeltaTable", side_effect=None)

        # Act
        silver_operations.prepareTarget(inDF)

        # Assert
        mock_alter_delta_table.assert_called_once_with(
            silver_operations.tgtDatabaseName,
            silver_operations.tgtTableName,
            "`col1` INT"
        )


    def test_prepareTarget_with_empty_add_columns(self, mocked_silver_operations_with_timestamp, mocker, spark_session):
        silver_operations = mocked_silver_operations_with_timestamp

        inDF = create_bronze_df(spark_session)
        existing_df = create_silver_df(spark_session)

        # Arrange
        mock_table_exists = mocker.patch("com.phida.main.SilverOperations.tableExists", return_value=True)
        mock_path_exists = mocker.patch("com.phida.main.SilverOperations.pathExists", return_value=True)
        mock_drop_columns = mocker.patch("com.phida.main.SilverOperations.dropColumns", return_value=inDF)
        mock_existing_df = mocker.patch("pyspark.sql.DataFrameReader.table", return_value=existing_df)
        mock_schema_data_type_diff = mocker.patch("com.phida.main.SilverOperations.schemaDataTypeDiff", return_value=[])
        mock_hive_ddl = mocker.patch("com.phida.main.SilverOperations.hiveDDL", return_value="")
        mock_alter_delta_table = mocker.patch("com.phida.main.SilverOperations.alterDeltaTable")

        # Act
        silver_operations.prepareTarget(inDF)

        # Assert
        mock_alter_delta_table.assert_not_called()
    

    def test_streamIntoDeltaTarget_with_available_now(self, mocked_silver_operations_with_timestamp, mocker, spark_session):

        silver_operations = mocked_silver_operations_with_timestamp

        streaming_df = spark_session.readStream.format("rate").load()
        
        # Arrange
        mock_silver_cleansing = mocker.patch.object(silver_operations, "silverCleansing", return_value=streaming_df)
        mock_prepare_target = mocker.patch.object(silver_operations, "prepareTarget", side_effect=None)
        mock_start = mocker.patch("pyspark.sql.streaming.DataStreamWriter.start")

        # Act
        silver_operations.streamIntoDeltaTarget()

        # Assert
        mock_silver_cleansing.assert_called_once()
        mock_prepare_target.assert_called_once()
        mock_start.assert_called_once_with(silver_operations.tgtTablePath)
    

    def test_streamIntoDeltaTarget_without_available_now(self, mocked_silver_operations_with_timestamp, mocker, spark_session):

        silver_operations = mocked_silver_operations_with_timestamp
        silver_operations.availableNow = "N"

        streaming_df = spark_session.readStream.format("rate").load()
        
        # Arrange
        mock_silver_cleansing = mocker.patch.object(silver_operations, "silverCleansing", return_value=streaming_df)
        mock_prepare_target = mocker.patch.object(silver_operations, "prepareTarget", side_effect=None)
        mock_start = mocker.patch("pyspark.sql.streaming.DataStreamWriter.start")

        # Act
        silver_operations.streamIntoDeltaTarget()

        # Assert
        mock_silver_cleansing.assert_called_once()
        mock_prepare_target.assert_called_once()
        mock_start.assert_called_once()
    


    def test_overwriteToDeltaTarget_for_first_run(self, mocked_silver_operations_without_timestamp, mocker, spark_session):
        
        silver_operations = mocked_silver_operations_without_timestamp
        source_df = create_bronze_df(spark_session)

        # Arrange
        mock_check_if_first_run = mocker.patch("com.phida.main.SilverOperations.checkIfFirstRun", return_value=True)
        mock_initial_multiline_read = mocker.patch("com.phida.main.SilverOperations.initialMultilineRead", return_value=source_df)
        mock_create_delta_table = mocker.patch("com.phida.main.SilverOperations.createDeltaTable")
        mock_write_dataframe_to_table = mocker.patch("com.phida.main.SilverOperations.writeDataframeToTable")
        # Act
        silver_operations.overwriteToDeltaTarget()

        # Assert
        mock_create_delta_table.assert_called_once_with(source_df, silver_operations.tgtTablePath, silver_operations.tgtDatabaseName, silver_operations.tgtTableName, silver_operations.tgtPartitionColumns)
        mock_write_dataframe_to_table.assert_called_once_with(silver_operations.tgtDatabaseName, silver_operations.tgtTableName, mocker.ANY, "overwriteSchema", "overwrite")


    def test_overwriteToDeltaTarget_for_not_first_run(self, mocked_silver_operations_without_timestamp, mocker, spark_session):
        silver_operations = mocked_silver_operations_without_timestamp
        source_df = create_bronze_df(spark_session)

        # Arrange
        mocker.patch("com.phida.main.SilverOperations.checkIfFirstRun", return_value=False)
        mocker.patch("com.phida.main.SilverOperations.initialMultilineRead", return_value=source_df)
        mock_write_dataframe_to_table = mocker.patch("com.phida.main.SilverOperations.writeDataframeToTable")
        mock_spark_sql = mocker.patch.object(spark_session, "sql")
        
        # Act
        silver_operations.overwriteToDeltaTarget()

        # Assert
        mock_write_dataframe_to_table.assert_called_once_with(silver_operations.tgtDatabaseName, silver_operations.tgtTableName, mocker.ANY, "overwriteSchema", "overwrite")    
