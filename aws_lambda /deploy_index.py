import boto3
import logging
import traceback

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

def lambda_handler(event, context):
    logger.info("Checking if Cluster is in Waiting state")
    try:
        # event from CloudWatch Event, triggers everytime a cluster state change to waiting occurs
        logger.info(print(event))
        if event['details']['state'] = "WAITING" or "RUNNING":
            emr_client = boto3.client('emr')
            ssm = boto3.client('ssm')
            clusters = emr_client.list_clusters()
             # choose the correct cluster
            clusters = [c["Id"] for c in clusters["Clusters"] 
                        if c["Status"]["State"] in ["RUNNING", "WAITING"]]
            print(clusters)
            logger.info("Getting the right cluster ID")
            cluster_id = clusters[0]
            master_instance = emr_client.list_instances(ClusterID=cluster_id, InstanceGroupTypes=['MASTER'])
            response = ssm.send_command(
                InstanceIDs= master_instance,
                DocumentName= 'AWS-RunShellScript',
                 Parameters={
                    "commands":[
                    "./home/hadoop/examples/deploy_index_BBmap.sh"
                    ]   
                }
            )
    except Exception as e:
        logger.error("Exception at some step in the process  " + str(e))
        traceback.print_exc()  