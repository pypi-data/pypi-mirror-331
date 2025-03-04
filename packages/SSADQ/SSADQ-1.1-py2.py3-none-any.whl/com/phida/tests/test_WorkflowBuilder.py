from collections import OrderedDict
import pytest

from com.phida.main.WorkflowBuilder import WorkflowBuilder

@pytest.fixture
def mocked_workflow_builder_with_jobid_not_null(mocker):
    mocker.patch.object(WorkflowBuilder, "__init__", return_value=None)

    workflow_builder = WorkflowBuilder()
    workflow_builder.inputDict = OrderedDict([('job_group_id', ['100_2', '100_1']),
                            ('job_id', ['907978472540106', '459635357894608']),
                            ('job_name',
                            ['DQ_Windchill_OPDM_RawToSilver_Biweekly_100_2',
                            'DQ_Windchill_BronzeToSilver_Biweekly_100_1']),
                            ('job_desc',
                            ['SSA job for raw file to silver data transfer that runs every Monday and Thursday',
                            'SSA job for bronze to silver data transfer that runs every Monday and Thursday']),
                            ('job_tags',
                            ["{'cost-centre': 'DQ', 'source_mechanism':'Windchill', 'layer':'Bronze', 'frequency':'biweekly', 'source_system':'DQ_OPDM_RawToSilver', 'job_group_id':'100_2'}",
                            "{'cost-centre': 'DQ', 'source_mechanism':'Windchill', 'layer':'Bronze', 'frequency':'biweekly', 'source_system':'DQ_BronzeToSilver', 'job_group_id':'100_1'}"]),
                            ('task_str',
                            ['[{"task_key":"windchill_b_dq_windchill_opdm_stor_device_char_mvw","job_cluster_key":"Silver_Streaming_Application","notebook_path":"/Base_Streaming_Notebooks/Merge/silver_merge","source_file_path":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/bronze/EUMDR/latest_raw_data/raw_data/OPDM_STOR_DEVICE_CHAR_MVW.csv","source_database":"qa_wb.ea","source_table":"b_dq_windchill_opdm_stor_device_char_mvw","target_database":"qa_wb.ea","target_table":"s_dq_windchill_opdm_stor_device_char_mvw","tgt_checkpoint":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/silver/ssa_checkpoints/windchill/opdm_stor_device_char_mvw","tgt_table_path":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/silver/windchill/opdm_stor_device_char_mvw","contains_timestamp":"N","trigger_available_now":"Y"},{"task_key":"windchill_b_dq_windchill_opdm_tradeitem_mvw","job_cluster_key":"Silver_Streaming_Application","notebook_path":"/Base_Streaming_Notebooks/Merge/silver_merge","source_file_path":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/bronze/EUMDR/latest_raw_data/raw_data/OPDM_TRADEITEM_MVW.csv","source_database":"qa_wb.ea","source_table":"b_dq_windchill_opdm_tradeitem_mvw","target_database":"qa_wb.ea","target_table":"s_dq_windchill_opdm_tradeitem_mvw","tgt_checkpoint":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/silver/ssa_checkpoints/windchill/opdm_tradeitem_mvw","tgt_table_path":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/silver/windchill/opdm_tradeitem_mvw","contains_timestamp":"N","trigger_available_now":"Y"}]',
                            '[{"task_key":"windchill_b_dq_windchill_organization","job_cluster_key":"Silver_Streaming_Application","notebook_path":"/Base_Streaming_Notebooks/Merge/silver_merge","source_file_path":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/bronze/EUMDR/latest_raw_data/raw_data/ORGANIZATION.csv","source_database":"qa_wb.ea","source_table":"b_dq_windchill_organization","target_database":"qa_wb.ea","target_table":"s_dq_windchill_organization","tgt_checkpoint":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/silver/ssa_checkpoints/windchill/organization","tgt_table_path":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/silver/windchill/organization","contains_timestamp":"Y","trigger_available_now":"Y","drop_column_list":"source_operation, src_key_cols"},{"task_key":"windchill_b_dq_windchill_legal_entity","job_cluster_key":"Silver_Streaming_Application","notebook_path":"/Base_Streaming_Notebooks/Merge/silver_merge","source_file_path":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/bronze/EUMDR/latest_raw_data/raw_data/LEGAL_ENTITY.csv","source_database":"qa_wb.ea","source_table":"b_dq_windchill_legal_entity","target_database":"qa_wb.ea","target_table":"s_dq_windchill_legal_entity","tgt_checkpoint":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/silver/ssa_checkpoints/windchill/legal_entity","tgt_table_path":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/silver/windchill/legal_entity","contains_timestamp":"Y","trigger_available_now":"Y","drop_column_list":"source_operation, src_key_cols"}]']),
                            ('job_cluster_str',
                            ['[{"dbr_version":"13.3.x-scala2.12","policy_id":"001135D91EE5F2EE","num_workers":"2","job_cluster_key":"Silver_Streaming_Application"}]',
                            '[{"dbr_version":"13.3.x-scala2.12","policy_id":"001135D91EE5F2EE","num_workers":"6","job_cluster_key":"Silver_Streaming_Application"}]']),
                            ('schedules_str',
                            ['{"quartz_cron_expression":"00 00 09 ? * MON,THU","timezone_id":"UTC","pause_status":"UNPAUSED"}',
                            '{"quartz_cron_expression":"00 00 09 ? * MON,THU","timezone_id":"UTC","pause_status":"UNPAUSED"}'])])
    workflow_builder.onFailureEmailList = ['abc.xyz@philips.com']
    workflow_builder.library = "StreamingApplicationDQ==1.0"

    return workflow_builder


@pytest.fixture
def mocked_workflow_builder_with_jobid_null(mocker):
    mocker.patch.object(WorkflowBuilder, "__init__", return_value=None)

    workflow_builder = WorkflowBuilder()
    workflow_builder.inputDict = OrderedDict([('job_group_id', ['100_2', '100_1']),
                              ('job_id', [None, None]),  # Set the values to None
                              ('job_name',
                               ['DQ_Windchill_OPDM_RawToSilver_Biweekly_100_2',
                                'DQ_Windchill_BronzeToSilver_Biweekly_100_1']),
                              ('job_desc',
                               ['SSA job for raw file to silver data transfer that runs every Monday and Thursday',
                                'SSA job for bronze to silver data transfer that runs every Monday and Thursday']),
                              ('job_tags',
                               ["{'cost-centre': 'DQ', 'source_mechanism':'Windchill', 'layer':'Bronze', 'frequency':'biweekly', 'source_system':'DQ_OPDM_RawToSilver', 'job_group_id':'100_2'}",
                                "{'cost-centre': 'DQ', 'source_mechanism':'Windchill', 'layer':'Bronze', 'frequency':'biweekly', 'source_system':'DQ_BronzeToSilver', 'job_group_id':'100_1'}"]),
                              ('task_str',
                               ['[{"task_key":"windchill_b_dq_windchill_opdm_stor_device_char_mvw","job_cluster_key":"Silver_Streaming_Application","notebook_path":"/Base_Streaming_Notebooks/Merge/silver_merge","source_file_path":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/bronze/EUMDR/latest_raw_data/raw_data/OPDM_STOR_DEVICE_CHAR_MVW.csv","source_database":"qa_wb.ea","source_table":"b_dq_windchill_opdm_stor_device_char_mvw","target_database":"qa_wb.ea","target_table":"s_dq_windchill_opdm_stor_device_char_mvw","tgt_checkpoint":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/silver/ssa_checkpoints/windchill/opdm_stor_device_char_mvw","tgt_table_path":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/silver/windchill/opdm_stor_device_char_mvw","contains_timestamp":"N","trigger_available_now":"Y"},{"task_key":"windchill_b_dq_windchill_opdm_tradeitem_mvw","job_cluster_key":"Silver_Streaming_Application","notebook_path":"/Base_Streaming_Notebooks/Merge/silver_merge","source_file_path":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/bronze/EUMDR/latest_raw_data/raw_data/OPDM_TRADEITEM_MVW.csv","source_database":"qa_wb.ea","source_table":"b_dq_windchill_opdm_tradeitem_mvw","target_database":"qa_wb.ea","target_table":"s_dq_windchill_opdm_tradeitem_mvw","tgt_checkpoint":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/silver/ssa_checkpoints/windchill/opdm_tradeitem_mvw","tgt_table_path":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/silver/windchill/opdm_tradeitem_mvw","contains_timestamp":"N","trigger_available_now":"Y"}]',
                                '[{"task_key":"windchill_b_dq_windchill_organization","job_cluster_key":"Silver_Streaming_Application","notebook_path":"/Base_Streaming_Notebooks/Merge/silver_merge","source_file_path":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/bronze/EUMDR/latest_raw_data/raw_data/ORGANIZATION.csv","source_database":"qa_wb.ea","source_table":"b_dq_windchill_organization","target_database":"qa_wb.ea","target_table":"s_dq_windchill_organization","tgt_checkpoint":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/silver/ssa_checkpoints/windchill/organization","tgt_table_path":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/silver/windchill/organization","contains_timestamp":"Y","trigger_available_now":"Y","drop_column_list":"source_operation, src_key_cols"},{"task_key":"windchill_b_dq_windchill_legal_entity","job_cluster_key":"Silver_Streaming_Application","notebook_path":"/Base_Streaming_Notebooks/Merge/silver_merge","source_file_path":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/bronze/EUMDR/latest_raw_data/raw_data/LEGAL_ENTITY.csv","source_database":"qa_wb.ea","source_table":"b_dq_windchill_legal_entity","target_database":"qa_wb.ea","target_table":"s_dq_windchill_legal_entity","tgt_checkpoint":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/silver/ssa_checkpoints/windchill/legal_entity","tgt_table_path":"abfss://wb-ea@az21q1datalakewe.dfs.core.windows.net/silver/windchill/legal_entity","contains_timestamp":"Y","trigger_available_now":"Y","drop_column_list":"source_operation, src_key_cols"}]']),
                              ('job_cluster_str',
                               ['[{"dbr_version":"13.3.x-scala2.12","policy_id":"001135D91EE5F2EE","num_workers":"2","job_cluster_key":"Silver_Streaming_Application"}]',
                                '[{"dbr_version":"13.3.x-scala2.12","policy_id":"001135D91EE5F2EE","num_workers":"6","job_cluster_key":"Silver_Streaming_Application"}]']),
                              ('schedules_str',
                               ['{"quartz_cron_expression":"00 00 09 ? * MON,THU","timezone_id":"UTC","pause_status":"UNPAUSED"}',
                                '{"quartz_cron_expression":"00 00 09 ? * MON,THU","timezone_id":"UTC","pause_status":"UNPAUSED"}'])])
    workflow_builder.onFailureEmailList = "['abc.xyz@philips.com']"
    workflow_builder.library = "StreamingApplicationDQ==1.0"

    return workflow_builder


class TestWorkflowBuilder:
    @staticmethod
    def test_createTask_with_available_now(mocked_workflow_builder_with_jobid_not_null):

        # Arrange
        taskKey = "task1"
        jobClusterKey = "cluster1"
        notebookPath = "/path/to/notebook"
        srcFilePath = "abfss://source/file/path"
        srcDatabaseName = "source_database"
        srcTableName = "source_table"
        tgtDatabaseName = "target_database"
        tgtTableName = "target_table"
        tgtCheckpoint = "abfss://target/checkpoint/path"
        tgtTablePath = "abfss://target/table/path"
        tgtPartitionColumns = "col1,col2"
        derivedColExpr = "col3 + col4"
        containsTimestamp = "Y"
        availableNow = "Y"
        dropColumnStr = "col5,col6"
        pruneColumn = "col7"
        pythonWhlPath = "/path/to/python/whl"
        library = "example-library"

        workflow_builder = mocked_workflow_builder_with_jobid_not_null

        # Act
        result = workflow_builder.createTask(
            taskKey, jobClusterKey, notebookPath, srcFilePath, srcDatabaseName, srcTableName,
            tgtDatabaseName, tgtTableName, tgtCheckpoint, tgtTablePath, tgtPartitionColumns,
            derivedColExpr, containsTimestamp, availableNow, dropColumnStr, pruneColumn,
            pythonWhlPath, library
        )

        # Assert
        expected_result = {
            "task_key": taskKey,
            "description": f"This task is for ingesting the data from Bronze layer {srcDatabaseName}.{srcTableName} \
            to Silver layer {tgtDatabaseName}.{tgtTableName}",
            "depends_on": [],
            "job_cluster_key": jobClusterKey,
            "notebook_task": {
                "notebook_path": notebookPath,
                "base_parameters": {
                    "src_file_path": srcFilePath,
                    "src_database_name": srcDatabaseName,
                    "src_table_name": srcTableName,
                    "tgt_database_name": tgtDatabaseName,
                    "tgt_table_name": tgtTableName,
                    "tgt_checkpoint": tgtCheckpoint,
                    "tgt_table_path": tgtTablePath,
                    "tgt_partition_columns": tgtPartitionColumns,
                    "derived_col_expr": derivedColExpr,
                    "contains_timestamp": containsTimestamp,
                    "trigger_available_now": availableNow,
                    "prune_column": pruneColumn,
                    "drop_column_list": dropColumnStr
                }
            },
            "timeout_seconds": 0,
            "max_retries": 0,
            "min_retry_interval_millis": 900000,
            "retry_on_timeout": "false",
            "libraries": [
                {
                    "pypi": {
                        "package": library
                    }
                }
            ]
        }
        assert result == expected_result


    @staticmethod
    def test_createTask_with_unavailable_now(mocked_workflow_builder_with_jobid_not_null):

        # Arrange
        taskKey = "task1"
        jobClusterKey = "cluster1"
        notebookPath = "/path/to/notebook"
        srcFilePath = "abfss://source/file/path"
        srcDatabaseName = "source_database"
        srcTableName = "source_table"
        tgtDatabaseName = "target_database"
        tgtTableName = "target_table"
        tgtCheckpoint = "abfss://target/checkpoint/path"
        tgtTablePath = "abfss://target/table/path"
        tgtPartitionColumns = "col1,col2"
        derivedColExpr = "col3 + col4"
        containsTimestamp = "Y"
        availableNow = "N" # Test with unavailable now
        dropColumnStr = "col5,col6"
        pruneColumn = "col7"
        pythonWhlPath = "/path/to/python/whl"
        library = "example-library"

        workflow_builder = mocked_workflow_builder_with_jobid_not_null

        # Act
        result = workflow_builder.createTask(
            taskKey, jobClusterKey, notebookPath, srcFilePath, srcDatabaseName, srcTableName,
            tgtDatabaseName, tgtTableName, tgtCheckpoint, tgtTablePath, tgtPartitionColumns,
            derivedColExpr, containsTimestamp, availableNow, dropColumnStr, pruneColumn,
            pythonWhlPath, library
        )

        # Assert
        expected_result = {
            "task_key": taskKey,
            "description": f"This task is for ingesting the data from Bronze layer {srcDatabaseName}.{srcTableName} \
            to Silver layer {tgtDatabaseName}.{tgtTableName}",
            "depends_on": [],
            "job_cluster_key": jobClusterKey,
            "notebook_task": {
                "notebook_path": notebookPath,
                "base_parameters": {
                    "src_file_path": srcFilePath,
                    "src_database_name": srcDatabaseName,
                    "src_table_name": srcTableName,
                    "tgt_database_name": tgtDatabaseName,
                    "tgt_table_name": tgtTableName,
                    "tgt_checkpoint": tgtCheckpoint,
                    "tgt_table_path": tgtTablePath,
                    "tgt_partition_columns": tgtPartitionColumns,
                    "derived_col_expr": derivedColExpr,
                    "contains_timestamp": containsTimestamp,
                    "trigger_available_now": availableNow,
                    "prune_column": pruneColumn,
                    "drop_column_list": dropColumnStr
                }
            },
            "timeout_seconds": 85800,
            "max_retries": -1,
            "min_retry_interval_millis": 900000,
            "retry_on_timeout": "false",
            "libraries": [
                {
                    "pypi": {
                        "package": library
                    }
                }
            ]
        }
        assert result == expected_result    


    @staticmethod
    def test_createJobCluster(mocked_workflow_builder_with_jobid_not_null):

        # Arrange
        jobClusterKey = "Silver_Streaming_Application"
        DBRVersion = "13.3.x-scala2.12"
        clusterPolicyId = "001135D91EE5F2EE"
        numWorkers = "2"

        workflow_builder = mocked_workflow_builder_with_jobid_not_null

        # Act
        result = workflow_builder.createJobCluster(jobClusterKey, DBRVersion, clusterPolicyId, numWorkers)

        # Assert
        expected_result = {
            "job_cluster_key": jobClusterKey,
            "new_cluster": {
                "spark_version": DBRVersion,
                "policy_id": clusterPolicyId,
                "num_workers": numWorkers
            }
        }
        assert result == expected_result


    @staticmethod
    def test_createJob(mocked_workflow_builder_with_jobid_not_null):

        # Arrange
        jobName = "TestJob"
        jobTags = ["{'tag1': 'value1', 'tag2': 'value2'}"]
        tasks = [
            {
                "task_key": "task1",
                "job_cluster_key": "cluster1",
                "notebook_path": "/path/to/notebook1",
                # ... other task details
            },
            {
                "task_key": "task2",
                "job_cluster_key": "cluster2",
                "notebook_path": "/path/to/notebook2",
                # ... other task details
            },
        ]
        jobClusters = [
            {
                "job_cluster_key": "cluster1",
                "new_cluster": {
                    "spark_version": "13.3.x-scala2.12",
                    "policy_id": "001135D91EE5F2EE",
                    "num_workers": "2",
                }
            },
            # ... other job cluster details
        ]
        jobSchedule = "0 0 * * *"
        onFailureEmailList = ["abc.xyz@example.com"]

        workflow_builder = mocked_workflow_builder_with_jobid_not_null

        # Act
        result = workflow_builder.createJob(jobName, jobTags, tasks, jobClusters, jobSchedule, onFailureEmailList)

        # Assert
        expected_result = {
            "name": jobName,
            "tags": jobTags,
            "tasks": tasks,
            "job_clusters": jobClusters,
            "schedule": jobSchedule,
            "format": "MULTI_TASK",
            "email_notifications": {
                "on_failure": onFailureEmailList,
                "no_alert_for_skipped_runs": "false"
            },
            "timeout_seconds": 85800
        }
        assert result == expected_result

    
    @staticmethod
    def test_editJob(mocked_workflow_builder_with_jobid_not_null):

        # Arrange
        jobId = "907978472540106"
        jobName = "EditedTestJob"
        jobTags = ["{'tag1': 'edited_value1', 'tag2': 'edited_value2'}"]
        tasks = [
            {
                "task_key": "edited_task1",
                "job_cluster_key": "edited_cluster1",
                "notebook_path": "/path/to/edited_notebook1",
                # ... other task details
            },
            {
                "task_key": "edited_task2",
                "job_cluster_key": "edited_cluster2",
                "notebook_path": "/path/to/edited_notebook2",
                # ... other task details
            },
        ]
        jobClusters = [
            {
                "job_cluster_key": "edited_cluster1",
                "new_cluster": {
                    "spark_version": "13.3.x-scala2.12",
                    "policy_id": "001135D91EE5F2EE",
                    "num_workers": "2",
                }
            },
            # ... other edited job cluster details
        ]
        jobSchedule = "0 0 * * *"
        onFailureEmailList = ["edited_abc.xyz@example.com"]

        workflow_builder = mocked_workflow_builder_with_jobid_not_null

        # Act
        result = workflow_builder.editJob(jobId, jobName, jobTags, tasks, jobClusters, jobSchedule, onFailureEmailList)

        # Assert
        expected_result = {
            "job_id": jobId,
            "new_settings": {
                "name": jobName,
                "tags": jobTags,
                "tasks": tasks,
                "job_clusters": jobClusters,
                "schedule": jobSchedule,
                "format": "MULTI_TASK",
                "email_notifications": {
                    "on_failure": onFailureEmailList,
                    "no_alert_for_skipped_runs": "false"
                },
                "timeout_seconds": 85800
            },
            "fields_to_remove": ['tasks']
        }
        assert result == expected_result

    
    @staticmethod
    def test_buildJob_with_jobid_null(mocked_workflow_builder_with_jobid_null, mocker):

        # Arrange
        workflow_builder = mocked_workflow_builder_with_jobid_null

        # Act
        result = workflow_builder.buildJob()

        # Assert
        assert len(result) == 2
        assert result[0]["name"] == "DQ_Windchill_OPDM_RawToSilver_Biweekly_100_2"
        assert result[1]["name"] == "DQ_Windchill_BronzeToSilver_Biweekly_100_1"


    @staticmethod
    def test_buildJob_with_jobid_not_null(mocked_workflow_builder_with_jobid_not_null, mocker):

        # Arrange
        workflow_builder = mocked_workflow_builder_with_jobid_not_null

        # Act
        result = workflow_builder.buildJob()

        # Assert
        assert len(result) == 2
        assert result[0]["new_settings"]["name"] == "DQ_Windchill_OPDM_RawToSilver_Biweekly_100_2"
        assert result[1]["new_settings"]["name"] == "DQ_Windchill_BronzeToSilver_Biweekly_100_1"