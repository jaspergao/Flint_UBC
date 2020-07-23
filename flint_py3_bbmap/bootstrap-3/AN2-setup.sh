#!/bin/bash


#	Exit immediately if a command exits with a non-zero exit status. -x verbose bash workflow
set -e -x

#	Default Data and Application directories in the worker nodes
APPS_DIR="/home/hadoop/apps"
BIODATA_DIR="/mnt/bio_data"
INDEX_DIR=$BIODATA_DIR"/index"

mkdir -p $APPS_DIR
mkdir -p $BIODATA_DIR
mkdir -p $INDEX_DIR

#	Versions of the tools we'll be installing
#   Old version "2.3.4.1"
BOWTIE_VERSION="2.4.1"
SAMTOOLS_VERSION="1.3.1"
BBMAP_VERSION="38.86"

SOURCE_BUCKET_NAME="flint-implementation"

# need to change permissions on object to see if s3 copy works or else go to path and change
# change object permission 

#	Bowtie
wget https://$SOURCE_BUCKET_NAME.s3.amazonaws.com/apps/bowtie2-$BOWTIE_VERSION-linux-x86_64.zip
unzip -d $APPS_DIR bowtie2-$BOWTIE_VERSION-linux-x86_64.zip
BOWTIE_DIR=$APPS_DIR"/bowtie2-"$BOWTIE_VERSION"-linux-x86_64"

#  BBMap
wget https://$SOURCE_BUCKET_NAME.s3.amazonaws.com/apps/BBMap_$BBMAP_VERSION.tar.gz
tar -xvzf BBMap_$BBMAP_VERSION.tar.gz -C $APPS_DIR
BBMAP_DIR=$APPS_DIR"/BBMap_"$BBMAP_VERSION

cd ~

# ---------------------------------------------- Environment Setup ----------------------------------------------------
#
#	Setup our bash_profile
echo "" >> ~/.bash_profile
echo "alias l='ls -lhF'" >> ~/.bash_profile

#	Add bowtie2 to the path
echo "" >> ~/.bashrc
printf '\n\n# Bowtie2\n' >> ~/.bashrc
printf 'PATH=$PATH:'$BOWTIE_DIR'/; export PATH\n' >> ~/.bashrc

#   Add BBMap to the path 
echo "" >> ~/.bashrc
printf '\n\n# BBMap\n' >> ~/.bashrc
printf 'PATH=$PATH:'$BBMAP_DIR'/; export PATH\n' >> ~/.bashrc

# -------------------------------------------------- Cert Keys --------------------------------------------------------
#
#	The certificate is used so we can login into the worker nodes.
#
CERT_NAME="Mohn_flint_NCalifornia.pem"
S3_CERT="//"$SOURCE_BUCKET_NAME"/certs/"$CERT_NAME

CERT_DIR="/home/hadoop/certs"
mkdir -p $CERT_DIR

aws s3 cp s3:$S3_CERT $CERT_DIR

LOCAL_CERT=$CERT_DIR"/"$CERT_NAME
chmod 400 $LOCAL_CERT

# ------------------------------------------------- Worker List -------------------------------------------------------
#
#	Copy the script that retrieves the Worker node ip addresses. Used for debugging.
#

SCRIPTS_DIR="/home/hadoop/scripts"
mkdir -p $SCRIPTS_DIR

WORKER_LIST_SCRIPT_NAME="get_worker_ip_list.sh"
S3_WORKER_LIST_SCRIPT_PATH="//"$SOURCE_BUCKET_NAME"/steps/"$WORKER_LIST_SCRIPT_NAME

aws s3 cp s3:$S3_WORKER_LIST_SCRIPT_PATH $SCRIPTS_DIR

LOCAL_WORKER_LIST_SCRIPT=$SCRIPTS_DIR"/"$WORKER_LIST_SCRIPT_NAME
chmod ug+rwx $LOCAL_WORKER_LIST_SCRIPT

# ---------------------------------------------- Flint Project Dir ----------------------------------------------------
#
#	As a convenience, we'll create the directory were we'll be droping the source code.
#
FLINT_HOME="/home/hadoop/flint"
mkdir -p $FLINT_HOME


# ------------------------------------------------ Python Libs --------------------------------------------------------
#
#   Some Python libraries are not pre-installed. So we have to install them as part of the Cluster provisioning step.
#   Since May 25th, 2020 Biopython 1.77 is released which no longer supports Python 2.7 
#   For EMR version 5.21 >, default python for pyspark is 3.6.x thus to install third party libraries we need pip-3.6

sudo pip-3.6 install boto3
sudo pip-3.6 install pathlib2
sudo pip-3.6 install "biopython==1.76"
sudo pip-3.6 install wheel
sudo pip-3.6 install pandas

# ------------------------------------------------ Spark Conf ---------------------------------------------------------
#
#   Copy the custom Spark configurations.
#
CUSTOM_CONFS="/home/hadoop/confs"
mkdir -p $CUSTOM_CONFS

S3_CUSTOM_CONFS="//"$SOURCE_BUCKET_NAME"/config_files"

LOG4J_NAME="log4j.properties"
LOG4J_CONF=$S3_CUSTOM_CONFS"/"$LOG4J_NAME

SPARK_CONF_DIR="/etc/spark/conf"

#   Copy the conf from S3 into the local filesystem
aws s3 cp s3:$LOG4J_CONF $CUSTOM_CONFS



