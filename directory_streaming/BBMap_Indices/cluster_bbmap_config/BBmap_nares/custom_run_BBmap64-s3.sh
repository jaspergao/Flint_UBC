#!/bin/bash

# ---------------------------------------------------------------------------------------------------------------------
#
#                                  		Florida International University
#
#   This software is a "Camilo Valdes Work" under the terms of the United States Copyright Act.
#   Please cite the author(s) in any work or product based on this material.
#
#   OBJECTIVE:
#	The purpose of this script is to show an example of how to run a Flint analysis job.
#
#   NOTES:
#   Please see the dependencies and/or assertions section below for any requirements.
#
#   DEPENDENCIES:
#		• Apache-Spark
#       • Python
#		• flint.py
#
#	AUTHOR:
#			Camilo Valdes (camilo@castflyer.com)
#			Florida International University (FIU)
#
#
# ---------------------------------------------------------------------------------------------------------------------

sudo pip install boto3

echo ""
echo "[" `date '+%m/%d/%y %H:%M:%S'` "]"
echo "[" `date '+%m/%d/%y %H:%M:%S'` "] Starting Test..."

#	Base location for the project
BASE_DIR='/mnt/bio_data'

PROJECT_DIR='/home/hadoop'

#	File with Samples we want to process.  The format of this file is JSON.
CONF_SAMPLES_JSON=$PROJECT_DIR'/examples/directory_streaming/configurations/custom_streaming_configuration-s3_bbmap_nares_output.json'


# --------------------------------------------------- Spark Cluster ---------------------------------------------------
#
#   Cluster particulars (URL, executors, etc.) are configured here.  From the Spark documentation "Unlike Spark
#   standalone and Mesos modes, in which the master’s address is specified in the --master parameter, in YARN mode
#   the ResourceManager’s address is picked up from the Hadoop configuration. Thus, the --master parameter is 'yarn'."
#

URL_FOR_SPARK_CLUSTER="yarn"

#   Amount of memory to allocate for the driver process. orignally 10
MEMORY_FOR_DRIVER="14G"

#   The number of cores that the Driver process will use. # originally 8 
NUMBER_OF_DRIVER_CORES="8"

#   The number of Executor processes to launch in each Worker node.
NUMBER_OF_EXECUTORS="65"

#   The number of cores that each Executor process will use. # originally 1
NUMBER_OF_EXECUTOR_CORES="1"

#   Amount of memory to allocate for the executor processes. # orignally 10 
MEMORY_FOR_EXECUTORS="12G"

# Cluster has 64 core nodes with 8 vCPU cores and 15 GB of RAM
# Set number of executor cores = 5 for max HDFS output
# Number of executors per instance =(8-1)/5 = 1 round down
# Executor memory = 15GB
# should set Driver core = Executor core
# NUmber of executors = 1 * 64 - 1 = 63


YARN_QUEUE="default"

DEPLOY_MODE="client"

KINESIS_LIB_PATH="/usr/lib/spark/external/lib/spark-streaming-kinesis-asl-assembly.jar"

echo "[" `date '+%m/%d/%y %H:%M:%S'` "]"

#
#	Submit the script to the cluster using "bin/spark-submit".
#
#
spark-submit    --jars ${KINESIS_LIB_PATH} \
                --master yarn \
                --deploy-mode client \
                --queue default \
				--num-executors $NUMBER_OF_EXECUTORS \
				--executor-cores $NUMBER_OF_EXECUTOR_CORES \
				--executor-memory $MEMORY_FOR_EXECUTORS \
				--driver-memory $MEMORY_FOR_DRIVER \
				--driver-cores $NUMBER_OF_DRIVER_CORES \
				--conf spark.driver.maxResultSize=12g \
                ${PROJECT_DIR}/flint.py --samples ${CONF_SAMPLES_JSON} \
					                    --output_s3  \
							   		    --verbose   \
										--sensitive \
										--coalesce_output \
					                    --report_all \
										--debug \
					                    --stream_dir


echo "[" `date '+%m/%d/%y %H:%M:%S'` "]"
echo "[" `date '+%m/%d/%y %H:%M:%S'` "] Example Finished."
echo "[" `date '+%m/%d/%y %H:%M:%S'` "]"
echo ""