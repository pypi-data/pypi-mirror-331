from pyspark.sql.utils import AnalysisException
from com.phida.main.DataConfig import SRC_KEY_COLS
from com.phida.main.profileVars import getTableProps
from com.phida.main.sparksession import spark, logger
from com.phida.main.utils import pathExists
import re
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, IntegerType, FloatType, StringType, LongType
from pyspark.sql import Row

def tableExists(dbName, tblName):
    """
    desc:
        A static function for checking whether a given table exists.
        spark.catalog.tableExists method does not exist in python
        Although the scala method can be accessed using _jsparkSession, it is better to avoid using it

    args:
        dbName: String
        tblName: String

    return:
        Boolean - returns True or if it doesn't exist raises an exception

    example:
        tableExists("<database name>", "vbak")

    tip:
        N/A
    """
    try:
        spark.read.table(dbName + "." + tblName)
        return True
    except AnalysisException:
        return False


def getKeyCols(dbName, tblName):
    """
    desc:
        A Function for getting the primary key cols from the given table
        (Works only if source table is Bronze and src_key_cols is present in the table)

    args:
        dbName: String - A database name that is available in the catalog
        tblName: String - A Table name that is available in the catalog

    return:
        keyCols: String - returns the value of the column "src_key_cols" in the latest record
        of the given bronze table

    example:
        getKeyCols("<database name>", "vbuk")

    tip:
        Make sure the table is a bronze table and has the columns "src_key_cols" and "src_commit_time"
    """
    try:
        keyCols = spark.read.table(dbName + "." + tblName) \
            .select(SRC_KEY_COLS) \
            .limit(1) \
            .first()[0]
        return keyCols

    except Exception:
        raise Exception(
            f"the column src_key_cols is not present in the given table {dbName}.{tblName}")


def hiveDDL(df, columnsToBeExcludedFromSchema=None):
    """
    desc:
        A static function for printing the schema of a given dataframe in hive DDL format.
        In scala, this can be achieved using df.schema.toDDL()
        but this function is not available on python without using _jdf()

    args:
        df: DataFrame - Just any spark dataframe

    return:
        ddl: String - the schema in hive ddl format as a string

    example:
        df = spark.read.table("<database name>.vbak")
        hiveDDL(df)

    tip:
        N/A
    """
    tbl_ddl = ""
    for columnName in df.dtypes:
        if columnsToBeExcludedFromSchema is None or columnName[0] not in columnsToBeExcludedFromSchema:
            tbl_ddl = tbl_ddl + "`" + columnName[0] + "`" + " " + columnName[1] + ","

    tbl_ddl = tbl_ddl.rstrip(",")

    return tbl_ddl


def hasColumn(df, columnName):
    """
    A Function for checking whether a given column exists in a given dataframe

    args:
        df: DataFrame - a spark dataframe
        columnName: String - Column name as a string

    return:
        BOOLEAN - true or False

    example:
        df = spark.read.table("<database name>.vbuk")
        hasColumn(df, "erdat")

    tip:
        N/A
    """
    try:
        df.select(columnName)
        return True
    except AnalysisException:
        return False


def dropColumns(df, columnList):
    """
    desc:
        A Function for dropping the given columns in a given dataframe

    args:
        df: DataFrame - a spark dataframe
        columnList: List - A List containing column names as string

    return:
        df: DataFrame - returns the dataframe after dropping all the given columns in the list if they exist

    example:
        df = spark.read.table("<database name>.vbuk")
        dropColumns(df, ["src_commit_time", "hvr_integ_key"])

    tip:
        N/A

    """
    for columnName in columnList:

        if hasColumn(df, columnName):
            df = df.drop(columnName)
        else:
            pass

    return df


def addDerivedColumns(df, colExprList):
    """
    desc:
        A static Function for adding a derived partition column to a given dataframe.
        The function make sure the original columns are enclosed in `` to support special characters in the name

    args:
        df: DataFrame - given dataframe
        colExprList: List - A valid python list of spark expressions

    return:
        dfOut: DataFrame - The given dataframe after adding all the given derived columns

    examples:
        df = spark.read.table("<database name>.vbuk")
        somelist = ["cast(MANDT as int) as mandt_int","substr('vbeln',1,3) as sub_vbeln"]
        addDerivedColumns(df, somelist)

    Tips:
        1. Make sure that the expressions inside the list are enclosed by double quotes
        2. Do not use double quotes inside an expression
        3. Provide an alias for the derived column expression using as
    """
    columnList = df.columns

    new_columnList = []
    for column in columnList:
        new_column = f"`{column}`"
        new_columnList.append(new_column)

    columnList = new_columnList

    for colExpr in colExprList:
        try:
            df.selectExpr(colExpr)
        except Exception:
            raise Exception("The given column expression is invalid")

        columnList.append(colExpr)

    dfOut = df.selectExpr(columnList)

    return dfOut


def getDerivedColumnsList(colExprList):
    """
    desc:
        A static function for getting the list of columns that are derived from a given expression list

    args:
        colExprList: List - A valid python list of spark expressions.

    return:
        columnsList: List - returns the column name alone using the alias "as"

    example:
        somelist = ["date_format(to_date(col('erdat'),'yyyyMMdd'),'yyyyMM')) as yrmnth",
        "substr(col('vbeln'),1,3) as sub_vbeln"]
        getDerivedColumnsList(df, somelist)

    Tips:
        1. Make sure that the expressions inside the list are enclosed by double quotes
        2. Do not use double quotes inside an expression
        3. Provide an alias for the derived column expression using as
    """

    derivedColumnsList = []
    for columnName in colExprList:
        split_columns = columnName.split(" as ")
        if len(split_columns) == 2:
            derivedColumnsList.append(split_columns[1].strip())
        else:
            raise ValueError("Invalid column expression: missing alias")

    return derivedColumnsList


def createDeltaTable(df, path, dbName, tblName, pCols=""):
    """
    desc:
        A static function for creating the target table using the given dataframe schema, database and table name

    args:
        df: DataFrame - A spark dataframe
        path: String - A path or an external location for the table
        dbName: String - Name of the database for creating the table
        tblName: String - Name of the table to be created
        pCols: String - partition columns as a string with the column names separated with a comma

    return:
        N/A - Does not return anything. Just creates the table on the catalog

    example:
        df = spark.read.table("<database name>.vbak").drop("src_commit_time")
        createDeltaTable(df, "/user/tmp/table/vbak", "<database name>", "vbak", "objectclas")

    tip:
        1. This function will only create an external table
        2. The table will be created with the below table properties:
            delta.autoOptimize.optimizeWrite = true,
            delta.tuneFileSizesForRewrites = true,
            delta.dataSkippingNumIndexedCols = 10,
            delta.enableChangeDataCapture = true"
    """
    tblDDL = hiveDDL(df)
    partitions = f" \n PARTITIONED BY ({pCols})" if pCols else ""
    tblProps = getTableProps()  # ProfileSpecific Table Properties

    createTable = (
        "CREATE TABLE IF NOT EXISTS {dbName}.{tblName} ({tblDDL}) \n"
        "USING DELTA {partitions} \n"
        "LOCATION \"{path}\" \n"
        "TBLPROPERTIES ({tblProps})"
    ).format(
        dbName=dbName,
        tblName=tblName,
        tblDDL=tblDDL,
        partitions=partitions,
        path=path,
        tblProps=tblProps
    )

    spark.sql(f"CREATE DATABASE IF NOT EXISTS {dbName}")
    spark.sql(createTable)


def schemaDiff(df1, df2):
    """
    desc:
        A static function for checking the difference between the schema of given 2 dataframes.
        df1 is the driving dataframe and hence is of importance. if there are extra columns in df2,
        that will not be identified by this function as this is not intended for that purpose

    args:
        df1: DataFrame - Given spark dataframe 1
        df2: DataFrame - Given spark dataframe 2

    return:
        df: DataFrame - returns a dataframe with the column,
        that are present in df1 but not in df2

    example:
        df1 = spark.read.table("<database name>.vbuk")
        df2 = spark.read.table("<database name>.vbuk")
        schemaDiff(df1,df1)

    Tips:
        1. Make sure that the first dataframe has got more columns than the second
    """
    diff_columns = set(df1.columns) - set(df2.columns)

    # Select only the differing columns from df1
    df = df1.select(*diff_columns)

    return df


def schemaDataTypeDiff(df1, df2):
    """
    desc:
        A static function for checking the difference of column data types of given 2 dataframes.
        The function only checks columns that are present in both dataframes. 
        If a column is present in one dataframe but not in the other, it will not be reflected here. 

    args:
        df1: DataFrame - Given spark dataframe 1
        df2: DataFrame - Given spark dataframe 2

    return:
        mismatched_columns: List - returns a list of column names,
        whose data types are different in the two given dataframes

    example:
        df1 = spark.read.table("<database name>.vbuk")
        df2 = spark.read.table("<database name>.vbuk")
        schemaDiff(df1,df2)
    """
    dtypes_dict_df1 = dict(df1.dtypes)
    dtypes_dict_df2 = dict(df2.dtypes)

    mismatched_columns = [
        col_name
        for col_name, dtype_df1 in dtypes_dict_df1.items()
            if col_name in dtypes_dict_df2
                if dtypes_dict_df2.get(col_name) != dtype_df1
    ]

    return mismatched_columns


def alterDeltaTable(dbName, tblName, addColumns):
    """
    desc:
        A Function for altering the target table if there is a schema change in the source

    args:
        dbName: String - Name of the database for creating the table
        tblName: String - Name of the table to be created
        addColumns: String - newly added columns along with dataty[e in hive DDL format

    return:
        N/A - Does not return anything. Just adds columns to the given table

    example:
        alterDeltaTable("<database name>", "vbak", "yrmnth DATE")

    tip:
        1. This function will only add the given columns to the table
    """

    try:
        spark.sql(f"ALTER TABLE {dbName}.{tblName} ADD COLUMNS ({addColumns})")
    except AnalysisException:
        raise Exception(f"The given table {dbName}.{tblName} does not exist")


def buildColumnsDict(df, dropColumnList):
    """
    desc:
        A Function for building a data dictionary using the columns in the dataframe. (Coverts a list to data dict).
        This is used in whenMatchedUpdate and whenNotMatchedInsert clause of merge

    args:
        df: DataFrame - A spark dataframe

    return:
        columnsDict : Dict{String: String} - returns a python Dictionary

    example:
        df = spark.read.table("<database name>.vbuk")
        buildColumnsDict(df)

    tip:
        N/A

    """

    df = dropColumns(df, dropColumnList)

    columnsDict = {"`" + column + "`": f"s.`{column}`" for column in df.columns}

    return columnsDict


def buildJoinCondition(keyColsList):
    """
    desc:
        A Function for building the join condition for the merge using the key columns

    args:
        keyColsList: List - A list containing the key columns for the source DataFrame

    return:
        condition : List - A List containing the key columns

    example:
        buildJoinCondition(["mandt","vbeln","kunnr"])

    tip:
        N/A
    """
    condition = ""

    for column in keyColsList:
        condition = condition + "t.`" + column + "` <=> " + "s.`" + column + "` AND "

    return condition[:-5]


def initialMultilineRead(path, sep, header):
    """
    desc:
        A Function for reading csv files into DataFrame, from external storage

    args:
        path: String - Path to the file
        sep: String - Separator on which the csv file is separated
        header: Boolean - Indicates whether the first row is header in the csv

    return:
        df : DataFrame - A Dataframe containing the data from the csv file

    example:
        multilineRead("dbfs/tmp/filepath", "|", True)

    tip:
        N/A
    """
    try:
        df = spark.read.format("csv") \
            .option("sep", sep) \
            .option("header", header) \
            .option("inferSchema", True) \
            .option("multiLine", True) \
            .option("ignoreTrailingWhiteSpace", True) \
            .option("encoding", "UTF-8") \
            .option("parserLib", "univocity") \
            .option("quote", '"') \
            .option("escape", '"') \
            .load(path)
        return df
    except AnalysisException as e:
        print(f"An error occurred while reading the file: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    
def hive_ddl_to_spark_schema(hive_ddl_schema):
    type_mapping = {
        'INT': IntegerType(),
        'FLOAT': FloatType(),
        'STRING': StringType(),
        'DOUBLE': FloatType(),
        'BIGINT': LongType(),
        'BOOLEAN': StringType()
    }

    column_definitions = hive_ddl_schema.split(',')
    column_info = []

    for col_def in column_definitions:
        col_def = col_def.strip()
        match = re.match(r"`(\w+)`\s+(\w+)", col_def)
        if match:
            col_name = match.group(1)
            col_type = match.group(2).upper()
            if col_type in type_mapping:
                column_info.append((col_name, type_mapping[col_type]))
            else:
                raise ValueError(f"Unsupported type: {col_type}")
        else:
            raise ValueError(f"Invalid column definition: {col_def}")

    return column_info

def multilineRead(path, ddlSchema, sep, header):
    """
    desc:
        A Function for reading csv files into DataFrame with the defined schema, from external storage

    args:
        path: String - Path to the file
        ddlSchema: String - String containing the DDL Schema for the data to be loaded
        sep: String - Separator on which the csv file is separated
        header: Boolean - Indicates whether the first row is header in the csv

    return:
        df : DataFrame - A Dataframe containing the data from the csv file

    example:
        multilineRead("dbfs/tmp/filepath", "|", True)

    tip:
        N/A
    """
    try:
        dff = spark.read.format("csv") \
            .option("sep", sep) \
            .option("header", header) \
            .option("multiLine", True) \
            .option("ignoreTrailingWhiteSpace", True) \
            .option("encoding", "UTF-8") \
            .option("parserLib", "univocity") \
            .option("quote", '"') \
            .option("escape", '"') \
            .load(path)

            
        schema_column_info = hive_ddl_to_spark_schema(ddlSchema)
        schema_struct = StructType([StructField(name, dtype, True) for name, dtype in schema_column_info])
        df = dff.select(*[col(name) for name, _ in schema_column_info if name in dff.columns])

        for name, dtype in schema_column_info:
            if name in df.columns:
                df = df.withColumn(name, col(name).cast(dtype))
    

        return df
    except AnalysisException as e:
        print(f"An error occurred while reading the file: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def checkIfFirstRun(tgtDatabaseName, tgtTableName, tgtTablePath):
    """
    desc:
        A Function to check if the delta table operation is first run or not

    args:
        tgtDatabaseName: String - Target Database Name (Will be created if not exists)
        tgtTableName: String - Target Table Name (Will be created if not exists)
        tgtTablePath: String - Target Table Path (so that the table is created as external)

    return:
        first_run: Boolean - True if target table does not exist, false otherwise

    example:
        writeDataframeToTable(tgtDatabaseName, tgtTableName, df, "mergeSchema", "append")

    tip:
        N/A
    """
    target_path_exists = pathExists(tgtTablePath)

    target_table_exists = tableExists(tgtDatabaseName, tgtTableName)

    if target_path_exists and not target_table_exists:
        raise Exception(f"phida_log: {tgtDatabaseName}.{tgtTableName} cannot be created"
                        f" because {tgtTablePath} already exists. Clean the path and run again.")

    first_run = False if target_table_exists else True
    return first_run


def writeDataframeToTable(tgtDatabaseName, tgtTableName, df, schema_operation, write_mode):
    """
    desc:
        A Function to write DF to target table

    args:
        tgtDatabaseName: String - Target Database Name (Will be created if not exists)
        tgtTableName: String - Target Table Name (Will be created if not exists)
        change_df: DataFrame - DataFrame created from source file
        schema_operation: String - Do you want to merge or overwrite schema?
        write_mode: String - Do you want to overwrite existing data or append on the table?

    return:
        None - Does not return anything

    example:
        writeDataframeToTable(tgtDatabaseName, tgtTableName, df, "mergeSchema", "append")

    tip:
        N/A
    """
    df.write \
        .format("delta") \
        .option(schema_operation, True) \
        .mode(write_mode) \
        .saveAsTable(f"{tgtDatabaseName}.{tgtTableName}")


def checkForSchemaChanges(source_df, existing_df, tgtDatabaseName, tgtTableName, columnsToBeAppendedInTarget):
    """
    desc:
        A Function for checking schema changes between the source file DF and the target bronze table DF

    args:
        source_df: Dataframe - The data loaded from source csv file
        existing_df: Dataframe - The data loaded from target delta table
        tgtDatabaseName: String - Target Database Name (Will be created if not exists)
        tgtTableName: String - Target Table Name (Will be created if not exists)
        columnsToBeAppendedInTarget: List - Columns to be added to source df and written to delta target tables

    return:
        None - Does not return anything

    example:
        see method ingestToBronzeTarget() for usage()

    tip:
        N/A
    """
    diff2_df = schemaDiff(existing_df, source_df)
    missing_cols = list(set(diff2_df.columns) - set(columnsToBeAppendedInTarget))
    if missing_cols:
        raise Exception(f"Column(s) {missing_cols} is(are) missing")

    mismatched_columns = schemaDataTypeDiff(existing_df, source_df)
    missing_cols = list(set(mismatched_columns) - set(columnsToBeAppendedInTarget))
    if missing_cols:
        raise Exception(f"There is data type mismatch in column(s): {missing_cols}")

    diff_df = schemaDiff(source_df, existing_df)
    add_columns = hiveDDL(diff_df)
    if add_columns:
        logger.info(f"phida_log: There seems to be a schema change in bronze")
        logger.info(f"phida_log: Altering the target table {tgtDatabaseName}.{tgtTableName}")

        alterDeltaTable(tgtDatabaseName, tgtTableName, add_columns)

        logger.info(f"phida_log: newly added columns {add_columns}")
    else:
        logger.info(f"phida_log: There is no change in schema in bronze")

def get_row_count(schema_table, where_clause):
    df = spark.sql(f"SELECT * AS count FROM {schema_table} WHERE tablename = '{where_clause}'")
    return df.count()

def get_ddl_schema(schema_table, where_clause):
    schema_entry = spark.sql(
        f"SELECT * FROM {schema_table} WHERE TableName = '{where_clause}'").first()
    ddl_schema = schema_entry['Columns']
    return ddl_schema

def insert_data(columnsToBeAppendedInBronze, target_df, srcFilePath, schema_table):
    schema = hiveDDL(target_df, columnsToBeAppendedInBronze)
    new_entry = Row(TableName=srcFilePath, Columns=schema)
    new_entry_df = spark.createDataFrame([new_entry])
    new_entry_df.write.format("delta").mode("append").saveAsTable(schema_table)
    return "Data inserted successfully"