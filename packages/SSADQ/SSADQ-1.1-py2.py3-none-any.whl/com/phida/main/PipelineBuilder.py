from collections import OrderedDict
import json

class PipelineBuilder:
    """
            A class for building Databricks pipelines with multiple parallel activities. This is ideal for automating SAP
            ingestion use cases where many tables are periodically ingested into delta lake using jobs

            args:
                inputDict: collections.OrderedDict - A single ordered dictionary containing all the possible configurations
                 for building the JSON in the databricks jobs API format

            methods:
                createPipeline
                createActivity
                createTrigger
                buildPipeline
                buildTrigger

            example:
                from com.phida.main.PipelineBuilder import PipelineBuilder
                pipelineBuilderObj = PipelineBuilder(dict)
                pipelineList = pipelineBuilderObj.buildPipeline()

    """
    def __init__(self,inputDict: OrderedDict):
        """"
                desc:
                Initialize the required variables for the class

                args:
                    inputDict: inputDict - A single ordered dictionary containing all the possible configurations
                     for building the JSON in the Azure Synapse API Version: 2020-12-01

                example:
                    # Sample data for inputDict argument:
                     orderedDict = OrderedDict([('pipeline_group_id', ['1_1', '1_2']),
             ('pipeline_name', ['mara t001 Daily', 'vbak vbap vbuk Hourly']),
             ('pipeline_desc',
              ['Silver Stream Application job that runs daily',
               'Silver Stream Application job that runs hourly']),
             ('activity_str',
              [
                  '[{"activity_key":"wpp_mara","notebook_name":"Silver Merge - mara","source_database":"prod_bronze_wpp","source_table":"mara","target_database":"prod_silver_wpp","target_table":"mara","tgt_checkpoint":"abfss://data@eacloud.dfs.core.windows.net/checkpoint_dir/prod_bronze_wpp/mara","tgt_table_path":"abfss://data@eacloud.dfs.core.windows.net/prod_silver_wpp/mara","contains_timestamp":"Y","trigger_available_now":"Y","drop_column_list":"hvr_integ_key, hvr_target_integrate_time, source_operation, src_key_col_values, src_key_cols"},{"activity_key":"wpp_t001","notebook_name":"Silver Merge - t001","source_database":"prod_bronze_wpp","source_table":"t001","target_database":"prod_silver_wpp","target_table":"t001","tgt_checkpoint":"abfss://data@eacloud.dfs.core.windows.net/checkpoint_dir/prod_bronze_wpp/t001","tgt_table_path":"abfss://data@eacloud.dfs.core.windows.net/prod_silver_wpp/t001","contains_timestamp":"Y","trigger_available_now":"Y","drop_column_list":"hvr_integ_key, hvr_target_integrate_time, source_operation, src_key_col_values, src_key_cols"}]',
                  '[{"activity_key":"wpp_vbak","notebook_name":"Silver Merge - vbak","source_database":"prod_bronze_wpp","source_table":"vbak","target_database":"prod_silver_wpp","target_table":"vbak","tgt_checkpoint":"abfss://data@eacloud.dfs.core.windows.net/checkpoint_dir/prod_bronze_wpp/vbak","tgt_table_path":"abfss://data@eacloud.dfs.core.windows.net/prod_silver_wpp/vbak","contains_timestamp":"Y","trigger_available_now":"Y","drop_column_list":"hvr_integ_key, hvr_target_integrate_time, source_operation, src_key_col_values, src_key_cols"},{"activity_key":"wpp_vbap","notebook_name":"Silver Merge - vbap","source_database":"prod_bronze_wpp","source_table":"vbap","target_database":"prod_silver_wpp","target_table":"vbap","tgt_checkpoint":"abfss://data@eacloud.dfs.core.windows.net/checkpoint_dir/prod_bronze_wpp/vbap","tgt_table_path":"abfss://data@eacloud.dfs.core.windows.net/prod_silver_wpp/vbap","contains_timestamp":"Y","trigger_available_now":"Y","drop_column_list":"hvr_integ_key, hvr_target_integrate_time, source_operation, src_key_col_values, src_key_cols"},{"activity_key":"wpp_vbuk","notebook_name":"Silver Merge - vbuk","source_database":"prod_bronze_wpp","source_table":"vbuk","target_database":"prod_silver_wpp","target_table":"vbuk","tgt_checkpoint":"abfss://data@eacloud.dfs.core.windows.net/checkpoint_dir/prod_bronze_wpp/vbuk","tgt_table_path":"abfss://data@eacloud.dfs.core.windows.net/prod_silver_wpp/vbuk","contains_timestamp":"Y","trigger_available_now":"Y","drop_column_list":"hvr_integ_key, hvr_target_integrate_time, source_operation, src_key_col_values, src_key_cols"}]']),
             ('spark_pool_str',
              ['[{"spark_pool_name":"SparkCompare","driverSize":"Small","executorSize":"Small","num_workers":"2"}]',
               '[{"spark_pool_name":"SparkCompare","driverSize":"Small","executorSize":"Small","num_workers":"4"}]']),
             ('schedules_str',
              [
                  '{"trigger_name":"Daily Trigger","frequency":"Hour","interval":"1","startTime":"2023-11-23T07:30:00Z","timeZone":"UTC"}',
                  '{"trigger_name":"Hourly Trigger","frequency":"Hour","interval":"1","startTime":"2023-11-23T07:30:00Z","timeZone":"UTC"}'])])

        """
        self.inputDict = inputDict

    def createPipeline(self,pipelineName,pipelineDesc,activities):
        """
        desc:
            This function is for creating the pipeline structure in the format of Azure Synapse API Version:
2020-12-01
        args:
            pipelineName: String - Name of the pipeline
            pipelineDesc: String - Pipeline Description
            activities: List - the list of all the Activity json body in the pipeline
        return:
            pipelineDict: Dict - returns the entire pipeline structure that was built using the Azure Synapse API Version: 2020-12-01
        """
        pipelineDict = {
            "properties": {
                "activities": activities,
                "description": pipelineDesc,
                "parameters": {
                    "pipelineName": {       #Custom Parameter for Dynamically Naming Pipeline
                        "type": "string",
                        "defaultValue": pipelineName
                    }
                }
            }
        }
        return pipelineDict

    def buildTrigger(self):
        """
                desc:
                    Builds the final trigger List format of Azure Synapse API Version: 2020-12-01
                args:
                    No args
                return:
                    triggerList: List - returns the List of triggers
        """

        pipelineRow = self.inputDict['pipeline_group_id']
        triggerList = []
        for index, key in enumerate(pipelineRow):
            pipelineName = self.inputDict["pipeline_name"][index]
            pipelineSchedule = json.loads(self.inputDict['schedules_str'][index])
            triggerList.append(self.createTrigger(pipelineName,pipelineSchedule))
        return triggerList
    def createTrigger(self,pipelineName,pipelineSchedule):

        """
                        desc:
                            Creates the trigger body in the format of Azure Synapse API Version: 2020-12-01
                        args:
                            pipelineName
                            pipelineSchedule
                        return:
                            triggerTouple: Touple - returns a touple with triggerTouple[0] ==  trigger_name and triggerTouple[1] == trigger Dictionary
        """

        triggerDict = {
            "properties": {
                "type": "ScheduleTrigger",
                "typeProperties": {
                    "recurrence": {
                        "frequency": pipelineSchedule["frequency"],
                        "interval": int(pipelineSchedule["interval"]),
                        "startTime": pipelineSchedule["startTime"],
                        "timeZone": pipelineSchedule["timeZone"]
                    }
                },
                "pipelines": [
                    {
                        "pipelineReference": {
                            "referenceName": pipelineName,
                            "type": "PipelineReference"
                        }
                    }
                ]
            }

        }
        triggerTouple = (pipelineSchedule["trigger_name"],triggerDict)
        return triggerTouple

    def createActivity(self,spark_pool_name, driverSize,executorSize,num_workers,
                       activityKey, notebookName, srcFilePath, srcDatabaseName, srcTableName,
                       tgtDatabaseName, tgtTableName, tgtCheckpoint, tgtTablePath, availableNow,
                       containsTimestamp, tgtPartitionColumns, derivedColExpr, pruneColumn,
                       dropColumnStr):

        """
                desc:
                    This function is for creating the Activity structure in the format of Azure Synapse API Version: 2020-12-01
                args:
                    spark_pool_name: String - Name spark pool
                    driverSize: String - Size of driver Node
                    executorSize: String - Size of executor Nodes
                    num_workers: String - Number of worker nodes
                    activityKey: String - A key for uniquely identifying a Activity
                    notebookName: String - Name of the Notebook to be executed.
                    srcFilePath: String - Source File Path(Raw Data File. Currently, supports only .csv files)
                    srcDatabaseName: String - Source Database (typically Bronze)
                    srcTableName: String - Source Table Name
                    tgtDatabaseName: String - Target Database Name (Will be created if not exists)
                    tgtTableName: String - Target Table Name (Will be created if not exists)
                    tgtCheckpoint: String - Target Checkpoint (For storing the status of the stream)
                    tgtTablePath: String - Target Table Path (so that the table is created as external)
                    availableNow: String - Whether availableNow or continuous streaming
                    containsTimestamp: String - Does the source file contain timestamp (Y or N)
                    tgtPartitionColumns: String - Target partition columns (optional)
                    derivedColExpr: String - Derived columns to be added to Silver (optional)
                    pruneColumn: String - Column for applying the prune filter in the merge ON condition clause \
                                  (to improve performance of the merge)
                    dropColumnStr: String - Columns to be dropped from source table df
                return:
                    activityDict: Dict - returns the Activity structure that was built using the Azure Synapse API Version: 2020-12-01
        """
        activityDict = {
            "name": activityKey,
            "type": "SynapseNotebook",
            "dependsOn": [],
            "policy": {
                "timeout": "0.12:00:00",
                "retry": 0,
                "retryIntervalInSeconds": 30,
                "secureOutput": False,
                "secureInput": False
            },
            "typeProperties": {
                "configurationType": "Default",
                "notebook": {
                    "referenceName": notebookName,
                    "type": "NotebookReference"
                },
                "sparkPool": {
                    "referenceName": spark_pool_name,
                    "type": "BigDataPoolReference"
                },
                "driverSize": driverSize,
                "executorSize": executorSize,
                "numExecutors": num_workers,
                "conf": {
                    "spark.dynamicAllocation.enabled": False,
                    "spark.dynamicAllocation.minExecutors": num_workers,
                    "spark.dynamicAllocation.maxExecutors": num_workers
                },
                "parameters": {
                    "srcDatabaseName": {
                        "value": srcDatabaseName,
                        "type": "string"
                    },
                    "srcTableName": {
                        "value": srcTableName,
                        "type": "string"
                    },
                    "tgtDatabaseName": {
                        "value": tgtDatabaseName,
                        "type": "string"
                    },
                    "tgtTableName": {
                        "value": tgtTableName,
                        "type": "string"
                    },
                    "tgtCheckpoint": {
                        "value": tgtCheckpoint,
                        "type": "string"
                    },
                    "tgtTablePath": {
                        "value": tgtTablePath,
                        "type": "string"
                    },
                    "tgtPartitionColumns": {
                        "value": tgtPartitionColumns,
                        "type": "string"
                    },
                    "derivedColExpr": {
                        "value": derivedColExpr,
                        "type": "string"
                    },
                    "pruneColumn": {
                        "value": pruneColumn,
                        "type": "string"
                    },
                    "availableNow": {
                        "value": availableNow,
                        "type": "string"
                    },
                    "dropColumnStr": {
                        "value": dropColumnStr,
                        "type": "string"
                    },
                    "srcFilePath": {
                        "value": srcFilePath,
                        "type": "string"
                    },
                    "containsTimestamp": {
                        "value": containsTimestamp,
                        "type": "string"
                    }
                }

            }
        }
        return activityDict


    def buildPipeline(self):

        """
        desc:
            Builds the final pipeline dictionary in the format of Azure Synapse API Version: 2020-12-01
        args:
            No args
        return:
            returns the entire pipeline structure in the jormat of Azure Synapse API Version: 2020-12-01 as a python data dictionary
        """

        pipelineRow = self.inputDict['pipeline_group_id']

        pipelineList = []
        for index, key in enumerate(pipelineRow):
            pipelineName = self.inputDict["pipeline_name"][index]
            pipelineDesc = self.inputDict["pipeline_desc"][index]
            pipelineSchedule = json.loads(self.inputDict['schedules_str'][index])
            # List of Spark Session Configurations
            sparkSessionConfigList = json.loads(self.inputDict['spark_pool_str'][index])
            sessionConfigs = []
            for sessionConfig in sparkSessionConfigList:
                spark_pool_name = sessionConfig["spark_pool_name"]
                driverSize = sessionConfig["driverSize"]
                executorSize = sessionConfig["executorSize"]
                num_workers = int(sessionConfig["num_workers"])
            # Create all the activities and store them in a list named "activityList"
            activityList = json.loads(self.inputDict['activity_str'][index])
            activities = []
            for activity in activityList:
                activityKey = activity['activity_key']
                notebookName = activity['notebook_name']
                try:
                    srcFilePath = activity['source_file_path']
                except:
                    srcFilePath = ""
                srcDatabaseName = activity['source_database']
                srcTableName = activity['source_table']
                tgtDatabaseName = activity['target_database']
                tgtTableName = activity['target_table']
                tgtCheckpoint = activity['tgt_checkpoint']
                tgtTablePath = activity['tgt_table_path']
                availableNow = activity['trigger_available_now']
                containsTimestamp = activity['contains_timestamp']
                try:
                    tgtPartitionColumns = activity['tgt_partition_columns']
                except:
                    tgtPartitionColumns = ""

                try:
                    derivedColExpr = activity['derived_col_expr']
                except:
                    derivedColExpr = ""

                try:
                    pruneColumn = activity['prune_column']
                except:
                    pruneColumn = ""

                try:
                    dropColumnStr = activity['drop_column_list']
                except:
                    dropColumnStr = ""

                activityTemp = self.createActivity( spark_pool_name, driverSize,executorSize,num_workers,
                                    activityKey, notebookName, srcFilePath, srcDatabaseName, srcTableName,
                                    tgtDatabaseName, tgtTableName, tgtCheckpoint, tgtTablePath, availableNow,
                                    containsTimestamp, tgtPartitionColumns, derivedColExpr, pruneColumn,
                                    dropColumnStr)
                activities.append(activityTemp)
            pipelineList.append(self.createPipeline(pipelineName,pipelineDesc, activities))
        return pipelineList