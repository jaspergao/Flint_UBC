


def lambda_handler(event, context):
    conn = boto3.client("emr")        
    cluster_id = conn.run_job_flow(
        Name='ClusterName',
        ServiceRole='EMR_DefaultRole',
        JobFlowRole='EMR_EC2_DefaultRole',
        VisibleToAllUsers=True,
        LogUri='s3n://some-log-uri/elasticmapreduce/',
        ReleaseLabel='emr-5.29.0',
        Instances={
            'InstanceGroups': [
                {
                    'Name': 'Master nodes',
                    'Market': 'ON_DEMAND',
                    'InstanceRole': 'MASTER',
                    'InstanceType': 'm3.xlarge',
                    'InstanceCount': 1,
                },
                {
                    'Name': 'Slave nodes',
                    'Market': 'ON_DEMAND',
                    'InstanceRole': 'CORE',
                    'InstanceType': 'm3.xlarge',
                    'InstanceCount': 2,
                }
            ],
            'Ec2KeyName': 'key-name',
            'KeepJobFlowAliveWhenNoSteps': False,
            'TerminationProtected': False
        },
        Applications=[{
            'Name': 'Spark'
        }],
        Configurations=[{
            "Classification":"spark-env",
            "Properties":{},
            "Configurations":[{
                "Classification":"export",
                "Properties":{
                    "PYSPARK_PYTHON":"python35",
                    "PYSPARK_DRIVER_PYTHON":"python35"
                }
            }]
        }],
        BootstrapActions=[{
            'Name': 'Install',
            'ScriptBootstrapAction': {
                'Path': 's3://path/to/bootstrap.script'
            }
        }],
        Steps=[{
            'Name': 'StepName',
            'ActionOnFailure': 'TERMINATE_CLUSTER',
            'HadoopJarStep': {
                'Jar': 's3n://elasticmapreduce/libs/script-runner/script-runner.jar',
                'Args': [
                    "/usr/bin/spark-submit", "--deploy-mode", "cluster",
                    's3://path/to/code.file', '-i', 'input_arg', 
                    '-o', 'output_arg'
                ]
            }
        }],
    )
    return "Started cluster {}".format(cluster_id)