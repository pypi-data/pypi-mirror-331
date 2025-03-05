from collections import OrderedDict
import json


class WorkflowBuilder:
    """
        A class for building Databricks workflow/jobs with multiple parallel tasks. This is ideal for automating SAP
        ingestion use cases where many tables are periodically ingested into delta lake using jobs

        args:
            inputDict: collections.OrderedDict - A single ordered dictionary containing all the possible configurations
             for building the JSON in the databricks jobs API format

        methods:
            createTask
            createJobCluster
            createJob
            buildJob
            executeJob

        example:
            from com.phida.main.WorkflowBuilder import WorkflowBuilder
            workflowObj = WorkflowBuilder(orderedDict)
            jobList = workflowObj.buildJob()

        """

    def __init__(self, inputDict: OrderedDict, onFailureEmailList: list, library: str):
        """"
        desc:
        Initialize the required variables for the class

        args:
            inputDict: inputDict - A single ordered dictionary containing all the possible configurations
             for building the JSON in the databricks jobs API format
            onFailureEmailList: List of string - A list of emails to be notified when a job failed
            library: string - PyPI library name with version number

        example:
            # Sample data for inputDict argument:
             orderedDict = OrderedDict([('job_group_id', [1, 2]),
             ('job_id', [None, None]),
             ('job_name', ['HVR_Batch_1_jobs', 'HVR_Batch_2_jobs']),
             ('job_desc',
              ['This is a databricks job for executing the ingestion job for 20 critical SAP tables with an SLA of \
              less than 10 minutes latency',
               'This is a databricks job for executing the ingestion job for 20 critical SAP tables with an SLA of \
               less than 10 minutes latency']),
             ('job_cluster_key',
              ['reusable_job_cluster1', 'reusable_job_cluster2']),
             ('task_list',
              [['vbak', 'vbuk'],
               ['marc', 'cdpos']]),
             ('src_file_path', ['file_xx1', 'file_xx2']),
             ('tgt_database', ['streaming', 'streaming']),
             ('base_path', ['/users/user1/', '/users/user1/']),
             ('notebook_path',
              ['/Users/user1@abc.com/Streaming_POC/ETL/silver_merge_package_test',
               '/Users/user1@abc.com/Streaming_POC/ETL/silver_merge_package_test']),
             ('dbr_version', ['10.4.x-scala2.12', '10.4.x-scala2.12']),
             ('driver_type', ['Standard_E8ds_v4', 'Standard_E8ds_v4']),
             ('worker_type', ['Standard_E8ds_v4', 'Standard_E8ds_v4']),
             ('num_workers', ['4', '4'])])
            # example of library argument: "SilverStreamingApplication==1.0"


        """
        self.inputDict = inputDict
        self.onFailureEmailList = onFailureEmailList
        self.library = library

    @staticmethod
    def createJobCluster(jobClusterKey, DBRVersion, clusterPolicyId, numWorkers):
        """
        desc:
            A method for creating the reusable job cluster

        args:
            jobClusterKey - a key for uniquely identifying a job cluster
            DBRVersion - the version of the databricks release to be used
            clusterPolicyId - Define the Id for the cluster policy for which table will be created in JSON
            numWorkers - The target database for writing the table or creating the metadata


        return:
            silverCleansedDF: dict - returns the task in jobs API format as a dictionary

        example:
            createTask("task1", "job_cluster_1", "/users/usr/notebook", "/opt/db","<source database name>", "<target database name>", "vbuk")

        tip:
            There are many either or parameters in this
            Either, enter numWorkers or autoScale as Y. Do no enter both
            When autoScale is Y, make sure that minWorkers and maxWorkers are present too
            Either enter workerType and driverType or driverInstancePoolId and instancePoolId.
            Do not enter values for all 4 parameters mentioned above.
        """
        jobClusterDict = {
            "job_cluster_key": jobClusterKey,
            "new_cluster": {
                "spark_version": DBRVersion,
                "policy_id": clusterPolicyId,
                "num_workers": numWorkers
            }
        }

        return jobClusterDict

    @staticmethod
    def createTask(taskKey, jobClusterKey, notebookPath, srcFilePath, tgtDatabaseName, tgtTableName,
                   tgtTablePath, tgtTableKeyColumns, tgtPartitionColumns, containsTimestamp, pythonWhlPath, library):
        """
        desc:
            A method for creating the dict/json for a single task

        args:
            taskKey: String - a key for uniquely identifying a task
            jobClusterKey: String - a key for uniquely identifying a job cluster
            notebookPath: String - exact/absolute path of the notebook
            srcFilePath: String - Source File Path (Raw ADLS dump)
            tgtDatabaseName: String - Target Database Name (Will be created if not exists)
            tgtTableName: String - Target Table Name (Will be created if not exists)
            tgtTablePath: String - Target Table Path (so that the table is created as external)
            tgtTableKeyColumns: String - Comma separated column names that form the primary key for target(bronze) table
            tgtPartitionColumns: String - Target partition columns (optional)
            triggerOnce: String - Whether continuous streaming or just once
            library: String - Library to be installed for the job (with version number)

        return:
            taskDict: dict - returns the task in jobs API format as a dictionary

        example:
            createTask("task1", "job_cluster_1", "/users/usr/notebook", "/opt/db","<source file path>", "<target database name>", "vbuk")

        tip:
            N/A
        """

        taskDict = {
            "task_key": taskKey,
            "description": f"This task is for ingesting the data from Raw data storage {srcFilePath} \
                to Bronze layer {tgtDatabaseName}.{tgtTableName}",
            "depends_on": [],
            "job_cluster_key": jobClusterKey,
            "notebook_task": {
                "notebook_path": notebookPath,
                "base_parameters": {
                    "src_file_path": srcFilePath,
                    "tgt_database_name": tgtDatabaseName,
                    "tgt_table_name": tgtTableName,
                    "tgt_table_path": tgtTablePath,
                    "tgt_table_key_columns": tgtTableKeyColumns,
                    "tgt_partition_columns": tgtPartitionColumns,
                    "contains_timestamp": containsTimestamp,
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

        return taskDict

    @staticmethod
    def createJob(jobName, jobTags, tasks, jobClusters, jobSchedule, onFailureEmailList):
        """
        desc:
            This function is for creating the job structure in the format of databricks jobs API 2.1
        args:
            jobName: String - Name of the job
            jobTags: String - tags associated with the job
            tasks: List - the list of all the tasks in the job
            jobClusters: List - list of all the reusable job clusters in the job
            jobSchedule: String - A cron schedule for the job
            onFailureEmailList: List of string - A list of emails to be notified when a job failed
        return:
            jobDict: Dict - returns the entire job structure that was built using the jobs API 2.1 format
        """
        jobDict = {
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

        return jobDict

    @staticmethod
    def editJob(jobId, jobName, jobTags, tasks, jobClusters, jobSchedule, onFailureEmailList):
        """
        desc:
            This function is for editing the job structure in the format of databricks jobs API 2.1. This is only \
            applicable for jobs that are already present with a valid job_id
        args:
            jobId: String - Unique job_id for the job (returned by the databricks jobs API 2.1)
            jobName: String - Name of the job
            jobTags: String - tags associated with the job
            tasks: List - the list of all the tasks in the job
            jobClusters: List - list of all the reusable job clusters in the job
            jobSchedule: String - A cron schedule for the job
            onFailureEmailList: List of string - A list of emails to be notified when a job failed
        return:
            jobDict: Dict - returns the entire job structure that was built using the jobs API 2.1 format
        """
        jobDict = {
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

        return jobDict

    def buildJob(self):
        """
        desc:
            Builds the final job dictionary in the jobs format API 2.1
        args:
            No args
        return:
            returns the job structure in the jobs API 2.1 format as a python data dictionary
        """
        jobRow = self.inputDict['job_group_id']

        jobDict = []
        for index, key in enumerate(jobRow):

            # jobGroupId = json.loads(self.inputDict['job_group_id'][index])
            try:
                jobId = self.inputDict['job_id'][index]
            except:
                jobId = None
            jobName = self.inputDict['job_name'][index]
            jobTags = json.loads(self.inputDict['job_tags'][index].replace("\'", "\""))
            jobSchedule = json.loads(self.inputDict['schedules_str'][index])

            # Create all the job clusters and store them in a list named "jobClusters"
            jobClusterList = json.loads(self.inputDict['job_cluster_str'][index])
            jobClusters = []
            for jobCluster in jobClusterList:
                jobClusterKey = jobCluster['job_cluster_key']
                DBRVersion = jobCluster['dbr_version']
                try:
                    numWorkers = jobCluster['num_workers']
                except:
                    numWorkers = None

                try:
                    clusterPolicyId = jobCluster['policy_id']
                except:
                    clusterPolicyId = None

                jobClusterTemp = self.createJobCluster(jobClusterKey, DBRVersion, clusterPolicyId, numWorkers)

                jobClusters.append(jobClusterTemp)

            # Create all the tasks and store them in a list named "tasks"
            taskList = json.loads(self.inputDict['task_str'][index])
            tasks = []
            for task in taskList:
                taskKey = task['task_key']
                jobClusterKey = task['job_cluster_key']
                notebookPath = task['notebook_path']
                srcFilePath = task['source_file_path']
                tgtDatabaseName = task['target_database']
                tgtTableName = task['target_table']
                tgtTablePath = task['tgt_table_path']
                tgtTableKeyColumns = task['target_table_key_columns']
                containsTimestamp = task['contains_timestamp']

                try:
                    tgtPartitionColumns = task['tgt_partition_columns']
                except:
                    tgtPartitionColumns = ""

                taskTemp = self.createTask(taskKey, jobClusterKey, notebookPath, srcFilePath,
                                           tgtDatabaseName, tgtTableName, tgtTablePath, tgtTableKeyColumns,
                                           tgtPartitionColumns, containsTimestamp, "", self.library)

                tasks.append(taskTemp)
            if jobId is None:
                jobDict.append(
                    self.createJob(jobName, jobTags, tasks, jobClusters, jobSchedule, self.onFailureEmailList))
            else:
                jobDict.append(
                    self.editJob(jobId, jobName, jobTags, tasks, jobClusters, jobSchedule, self.onFailureEmailList))

        return jobDict
