import boto3
import logging
import traceback
import time 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

def lambda_handler(event, context):
    logger.info("Checking if Cluster is in Waiting state")
    try:
        # event from CloudWatch Event, triggers everytime a cluster state change to waiting occurs
        logger.info(print(event))
        if event['detail']['state'] == 'WAITING':
            logger.info("Has entered Waiting State...")
            emr_client = boto3.client('emr')
            ssm = boto3.client('ssm')
            logger.info("Getting the right cluster ID")
            cluster_id = event['detail']['clusterId']
            # currently does not return the only the master instance but rather a response
            instances = emr_client.list_instances(ClusterId=cluster_id, InstanceGroupTypes=['MASTER'])
            logger.info(print(instances))
            l = [i["Ec2InstanceId"] for i in instances["Instances"]]
            logger.info(print(l))
            master_instance = l 
            response = ssm.send_command(
                InstanceIds= l,
                DocumentName= 'AWS-RunShellScript',
                #TimeoutSeconds= 120,
                 Parameters={
                    "commands":[
                    "sh /home/hadoop/examples/deploy_index_BBmap.sh"
                    ]   
                }
            )
            # wait for command to run on master node 
            time.sleep(35)
            logger.info("[" + time.strftime('%d-%b-%Y %H:%M:%S', time.localtime()) + "] Sucessfully called deploy_index_BBmap")
    except Exception as e:
        logger.error("Exception at some step in the process  " + str(e))
        traceback.print_exc()  