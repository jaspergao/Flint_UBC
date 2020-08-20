import boto3
import emr_configuration_and_steps
import logging
import traceback

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')


def create_emr(name):
    try:
        emr = boto3.client('emr', region_name= 'us-west-1')
        cluster_id = emr.run_job_flow(
            Name=name,
            VisibleToAllUsers=emr_configuration_and_steps.visible_to_all_users,
            LogUri=emr_configuration_and_steps.log_uri,
            ReleaseLabel=emr_configuration_and_steps.release_label,
            Applications=emr_configuration_and_steps.applications,
            Instances=emr_configuration_and_steps.instances,
            Steps=emr_configuration_and_steps.steps,
            BootstrapActions=emr_configuration_and_steps.bootstrap_actions,
            Configurations=emr_configuration_and_steps.configurations,
            ScaleDownBehavior=emr_configuration_and_steps.scale_down_behavior,
            ServiceRole=emr_configuration_and_steps.service_role,
            JobFlowRole=emr_configuration_and_steps.job_flow_role,
            AutoScalingRole=emr_configuration_and_steps.auto_scaling_role,
            EbsRootVolumeSize=emr_configuration_and_steps.ebsRootVolumeSize
        )
        logger.info("EMR is created successfully")
        return cluster_id['JobFlowId']
    except Exception as e:
        traceback.print_exc()
        raise Exception(e)


def lambda_handler(event, context):
    logger.info("Starting the lambda function for spawning EMR")
    try:
        emr_cluster_id = create_emr('BBMap_Meiji')
        logger.info("emr_cluster_id is = " + emr_cluster_id)
    except Exception as e:
        logger.error("Exception at some step in the process  " + str(e))