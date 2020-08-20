visible_to_all_users = True
log_uri = 's3://aws-logs-970230676797-us-west-1/elasticmapreduce/'
release_label = 'emr-5.29.0'
applications = [
    {
        'Name': 'Spark'
    },  
    {
        'Name': 'Hadoop'
    }
]

instances = {
    'Ec2KeyName': 'jasperMohnLab',
    'Ec2SubnetId': 'subnet-05fb2a63',
    'EmrManagedMasterSecurityGroup': 'sg-0c17a6cf02648e9ad',
    'EmrManagedSlaveSecurityGroup': 'sg-0e1b3fc876b5bf30c',
    'InstanceGroups': [
                {
                    'Name': 'Master nodes',
                    'Market': 'SPOT',
                    'InstanceRole': 'MASTER',
                    'InstanceType': 'c4.2xlarge',
                    'InstanceCount': 1,
                },
                {
                    'Name': 'Slave nodes',
                    'Market': 'SPOT',
                    'InstanceRole': 'CORE',
                    'InstanceType': 'c4.2xlarge',
                    'InstanceCount': 64,
                }
            ],
    'KeepJobFlowAliveWhenNoSteps': True
}
steps = [
    {
        'Name': 'Setup Hadoop Debugging',
        'ActionOnFailure': 'TERMINATE_CLUSTER',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': ['state-pusher-script']
        }
    },
    {
        'Name': 'Setup Hadoop File System from S3',
        'ActionOnFailure':'CONTINUE',
        'HadoopJarStep': {
            'Jar': 's3://us-west-1.elasticmapreduce/libs/script-runner/script-runner.jar',
            'Args': [
                's3://flint-implementation/flint-master/amazon-emr/steps/first-step.sh'
            ]
        }
    },
    {
        "Name": "Indexing Reference",
        "ActionOnFailure": 'TERMINATE_CLUSTER',
        'HadoopJarStep': {
            "Jar": "command-runner.jar",
            "Args": [
                "spark-submit",
                "--deploy-mode",
                "cluster",
                "--driver-memory", "4g",
                "--executor-memory", "4g",
                "--executor-cores", "2",
                "--class", "your-main-class-full-path-name",
                "s3://your-jar-path-SNAPSHOT-jar-with-dependencies.jar"
            ]
        }
    },
    {
        "Name": "Running FLINT",
        "ActionOnFailure": 'TERMINATE_CLUSTER',
        'HadoopJarStep': {
            "Jar": "command-runner.jar",
            "Args": [
                "spark-submit",
                "--deploy-mode",
                "cluster",
                "--driver-memory", "4g",
                "--executor-memory", "4g",
                "--executor-cores", "2",
                "--class", "your-main-class-full-path-name",
                "s3://your-jar-path-SNAPSHOT-jar-with-dependencies.jar"
            ]
        }
    },
]

bootstrap_actions = [
    {
        'Name':'Install',
        'ScriptBootstrapAction':{
            'Path':'s3://flint-implementation/flint-master/amazon-emr/bootstrap_actions/AN2-setup.sh'
        }
    },
]

configurations = [
    {
        "Classification": "spark-log4j",
        "Properties": {
            "log4j.logger.root": "INFO",
            "log4j.logger.org": "INFO",
            "log4j.logger.com": "INFO"
        }
    },
    {
        "Classification":"spark",
        "Properties":{
            "maximizeResourceAllocation":"true"
        }
    },
    {
        "Configurations":
        [
            {
                "Classification":"export",
                "Properties":{
                    "PYSPARK_PYTHON":"/usr/bin/python3"
                    }
                }
        ],
        "Classification":"spark-env",
        "Properties":{}
    },
    {
        "Classification":"yarn-site",
        "Properties":{
            "yarn.nodemanager.resource.memory-mb":"15000",
            "yarn.nodemanager.pmem-check-enabled":"false",
            "yarn.scheduler.maximum-allocation-mb":"15000",
            "yarn.nodemanager.vmem-check-enabled":"false"}
    }
]
scale_down_behavior = 'TERMINATE_AT_TASK_COMPLETION'
service_role = 'EMR_DefaultRole'
job_flow_role = 'EMR_EC2_DefaultRole'
auto_scaling_role = 'EMR_AutoScaling_DefaultRole'
ebsRootVolumeSize=10