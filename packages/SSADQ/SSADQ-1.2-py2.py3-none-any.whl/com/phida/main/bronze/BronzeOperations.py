import datetime
from pyspark.sql import Row


from pyspark.sql import Window
from pyspark.sql.functions import lit, to_timestamp, row_number, col
from pyspark.sql.utils import AnalysisException
from pyspark.sql.types import StructType

from com.phida.main.DataConfig import SOURCE_OPERATION, ADLS_LOADED_DATE, OPERATION_INSERT, SRC_KEY_COLS, \
    OPERATION_UPDATE, UPDATESTAMP, MON_DATE_YEAR_HR_MN_SEC, OPERATION_DELETE, MON_DATE_YEAR
from com.phida.main.Operations import createDeltaTable, hiveDDL, initialMultilineRead, multilineRead, checkIfFirstRun, \
    writeDataframeToTable, checkForSchemaChanges, schemaDataTypeDiff, get_row_count,get_ddl_schema,insert_data
from com.phida.main.sparksession import logger, spark
from com.phida.main.utils import filePathExists, convertStrToList


class BronzeOperations:
    """
    A pipeline to help transfer full load data from RAW csv files to delta Bronze tables

    args:
        srcFilePath: String - Source File (Raw Data File)
        tgtDatabaseName: String - Target Database Name (Will be created if not exists)
        tgtTableName: String - Target Table Name (Will be created if not exists)
        tgtTablePath: String - Target Table Path (so that the table is created as external)
        tgtTableKeyColumns: String - Column names separated by comma to help identify the primary key for the
                                     target table
        tgtPartitionColumns: String - Target partition columns (optional)
        containsTimestamp: String - Does the source file contain timestamp(Y or N)

    methods:
        bronzeCleansing
        prepareTarget

    example:
        from com.phida.main.bronze.BronzeAppend import BronzeAppend
        bronzeAppendObj = BronzeAppend(srcFilePath, tgtDatabaseName, tgtTableName,
                                        tgtTablePath, tgtTableKeyColumns, tgtPartitionColumns, containsTimestamp)

    """

    def __init__(self, srcFilePath, tgtDatabaseName, tgtTableName, tgtTablePath, tgtTableKeyColumns,
                 tgtPartitionColumns, containsTimestamp):
        """
        desc:
            Initialize the required class variables

        args:
            srcFilePath: String - Source File Path(Raw Data File. Currently, supports only .csv files)
            tgtDatabaseName: String - Target Database Name (Will be created if not exists)
            tgtTableName: String - Target Table Name (Will be created if not exists)
            tgtTablePath: String - Target Table Path (so that the table is created as external)
            tgtTableKeyColumns: String - Column names separated by comma to help identify the primary key
                                         for the target table
            tgtPartitionColumns: String - Target partition columns (optional)
            containsTimestamp: String - Does the source file contain timestamp(Y or N)

        """

        logger.info("phida_log: Initialising class variables for raw to bronze delta transfer")

        self.srcFilePath = srcFilePath
        self.tgtDatabaseName = tgtDatabaseName
        self.tgtTableName = tgtTableName
        self.tgtTablePath = tgtTablePath
        self.tgtTableKeyColumns = tgtTableKeyColumns
        self.tgtPartitionColumns = tgtPartitionColumns
        self.containsTimestamp = (containsTimestamp == "Y")

        if filePathExists(self.srcFilePath):
            logger.info(f"phida_log: source file exists")
            logger.info(f"phida_log: initialising derived class variables")

            self.keyColsList = convertStrToList(self.tgtTableKeyColumns, ",")

            utc_now = datetime.datetime.utcnow()
            self.currentDate = utc_now.strftime(MON_DATE_YEAR)

            if self.containsTimestamp:
                self.columnsToBeAppendedInBronze = [SOURCE_OPERATION, SRC_KEY_COLS, ADLS_LOADED_DATE]
            else:
                self.columnsToBeAppendedInBronze = [ADLS_LOADED_DATE]

    def prepareCombinedDataframe(self, source_df, target_df):
        """
        desc:
            A Function to identify and combine all the changes b/w source DF and target DF

        args:
            source_df: DataFrame - DataFrame created from source file
            target_df: DatFrame - DataFrame created from target table

        return:
            None - DataFrame with identified inserts, updates and deletes

        example:
            prepareCombinedDataframe(source_df, target_df)

        tip:
            N/A
        """
        try:
            inserts_df = source_df.join(target_df, self.keyColsList, "leftanti") \
                .withColumn(SOURCE_OPERATION, lit(OPERATION_INSERT))  
            
            updates_df = source_df.alias("source") \
                .join(target_df.alias("target"), self.keyColsList) \
                .select("source.*") \
                .filter(to_timestamp(col(f"source.{UPDATESTAMP}"), MON_DATE_YEAR_HR_MN_SEC) >
                        to_timestamp(col(f"target.{UPDATESTAMP}"), MON_DATE_YEAR_HR_MN_SEC)) \
                .withColumn(SOURCE_OPERATION, lit(OPERATION_UPDATE))
            
            combined_df = inserts_df.union(updates_df) \
                .withColumn(SRC_KEY_COLS, lit(self.tgtTableKeyColumns)) \
                .withColumn(ADLS_LOADED_DATE, lit(self.currentDate))
            
            deletes_df = target_df.join(source_df, self.keyColsList, "leftanti") \
                .withColumn(SOURCE_OPERATION, lit(OPERATION_DELETE)) \
                .withColumn(SRC_KEY_COLS, lit(self.tgtTableKeyColumns)) \
                .withColumn(ADLS_LOADED_DATE, lit(self.currentDate))
            
            combined_df = combined_df.union(deletes_df)

            return combined_df
        except AnalysisException as e:
            raise RuntimeError(f"An error occurred while preparing the combined DataFrame: {e}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}")

    def appendChangesToBronze(self, source_df, target_df):
        """
        desc:
            A Function to help in appending change data into the bronze target

        args:
            None

        return:
            None - Does not return anything

        example:
            appendChangesToBronze()

        tip:
            N/A
        """
        window_spec = Window.partitionBy(*self.keyColsList).orderBy(
            to_timestamp(target_df.UPDATESTAMP, MON_DATE_YEAR_HR_MN_SEC).desc())

        target_filtered_df = target_df.withColumn("row_num", row_number().over(window_spec)) \
            .filter("row_num == 1") \
            .filter(target_df.source_operation != OPERATION_DELETE) \
            .drop("row_num")

        combined_df = self.prepareCombinedDataframe(source_df, target_filtered_df)

        writeDataframeToTable(self.tgtDatabaseName, self.tgtTableName, combined_df, "mergeSchema", "append")

        logger.info(f"phida_log: Appends data added into bronze table {self.tgtDatabaseName}.{self.tgtTableName}")

    def ingestToBronzeTarget(self):
        """
        desc:
            A Function for appending the records from the source into delta Target table

        args:
            None

        return:
            None - Does not return anything

        example:
            ingestToBronzeTarget()

        tip:
            Make sure the values provided in the notebook are correct
        """

        logger.info(f"phida_log: preparing the target delta table ")

        first_run = checkIfFirstRun(self.tgtDatabaseName, self.tgtTableName, self.tgtTablePath)
        schema_table = f"{self.tgtDatabaseName}.s_dq_schema_table"

        if first_run:
            logger.info(f"phida_log: This seems to be the first run")
            logger.info(f"phida_log: creating the target table {self.tgtDatabaseName}.{self.tgtTableName}")

            source_df = initialMultilineRead(self.srcFilePath, "|", True)

            createDeltaTable(source_df,
                             self.tgtTablePath,
                             self.tgtDatabaseName,
                             self.tgtTableName,
                             self.tgtPartitionColumns)

            if self.containsTimestamp:
                raw_refined_df = source_df.withColumn(SOURCE_OPERATION, lit(OPERATION_INSERT).cast("string")) \
                    .withColumn(SRC_KEY_COLS, lit(self.tgtTableKeyColumns).cast("string")) \
                    .withColumn(ADLS_LOADED_DATE, lit(self.currentDate).cast("string"))
            else:
                raw_refined_df = source_df.withColumn(ADLS_LOADED_DATE, lit(self.currentDate).cast("string"))

            writeDataframeToTable(self.tgtDatabaseName, self.tgtTableName, raw_refined_df,
                                  "overwriteSchema", "overwrite")

            logger.info(
                f"phida_log: first write into bronze table {self.tgtDatabaseName}.{self.tgtTableName} completed")
        else:
            target_df = spark.read.table(self.tgtDatabaseName + "." + self.tgtTableName)

            count = get_row_count(schema_table, self.srcFilePath)

            if count == 0:
                response = insert_data(self.columnsToBeAppendedInBronze, target_df, self.srcFilePath,
                                     schema_table)
                logger.info(
                    f"phida_log: {response} for {self.tgtDatabaseName}.{self.tgtTableName} is completed")

            ddl_schema = get_ddl_schema(schema_table, self.srcFilePath)
            source_df = multilineRead(self.srcFilePath,ddl_schema,  "|", True)

            mismatched_column = schemaDataTypeDiff(target_df, source_df)
            mismatched_columns = list(set(mismatched_column) - set(self.columnsToBeAppendedInBronze))

            if mismatched_columns:
                target_schema = target_df.schema

                target_column_types = {field.name: field.dataType for field in target_schema}

                updated_columns = []

                for col_name in source_df.columns:
                    if col_name in mismatched_columns:
                        target_type = target_column_types.get(col_name)
                        if target_type:
                            updated_columns.append(col(col_name).cast(target_type).alias(col_name))
                        else:
                            raise ValueError(f"Column '{col_name}' not found in target_df schema.")
                    else:
        # If the column is not in mismatched_columns, keep it as is
                        updated_columns.append(col(col_name))

                source_df = source_df.select(*updated_columns)
            else:
                source_df = source_df



            checkForSchemaChanges(source_df, target_df, self.tgtDatabaseName, self.tgtTableName,
                                  self.columnsToBeAppendedInBronze)

            logger.info(f"phida_log: Appending data change to bronze table {self.tgtDatabaseName}.{self.tgtTableName}")

            if self.containsTimestamp:
                self.appendChangesToBronze(source_df, target_df)
            else:
                writeDataframeToTable(self.tgtDatabaseName, self.tgtTableName, source_df, "mergeSchema", "append")
