#!/usr/bin/env python3
# coding: utf-8
import boto3
import json 
import paramiko
import time 
import itertools
import subprocess as sp 
import urllib.parse


print("[" + time.strftime('%d-%b-%Y %H:%M:%S', time.localtime()) + "] Preparing to Interleave Files...")
s3 = boto3.client('s3')
ec2 = boto3.client('ec2', region_name='us-west-1')
bucket_name = "flint-implementation/reads/interleave/"


def lambda_handler(event, handler):
    start_ec2_instance()


    return {
        'statusCode': 200,
        'body': json.dumps('file is created in:'+s3_path)
    }
    

    try:
        response = s3.get_object(Bucket= bucket, Key=key)
        text = response["Body"].read()
    
    
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. \
        Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))


def start_ec2_instance():
    '''
    Create a new Amazon AMI Linux EC2 instance to process/reformat mate files
    '''



def interleave_with_bbmap(iterator):

        #   Obtain a properly formatted Bowtie2 command.
        bbmapCMD = getBBMAPCommand(bbmap_node_path=bowtie2_node_path,
                                   bbmap_index_path=bowtie2_index_path,
                                   bbmap_index_name=bowtie2_index_name,
                                   bbmap_number_threads=bowtie2_number_threads)

        #   Open a pipe to the subprocess that will launch the BBmap aligner.
        try:
            interleave_subprocess = sp.Popen(bbmapCMD, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
            interleave_output, interleave_error = align_subprocess.communicate(input="\n".join(reads_list))
            


        except sp.CalledProcessError as err:
            print( "[BBmap - INTERLEAVE ERROR] " + str(err))
            sys.exit(-1)

        return iter(alignments)
    
    def getBBMAPCommand(bbmap_node_path, bbmap_index_name, bbmap_number_threads):
        """
        Constructs a properly formmated shell BBMap command by taking in FASTQ files from stdin. 
        Returns:
            An array of BBMap flags and arguments back to popen() function.

        """

        R1 = "path"
        R2 = "path"
    
        bbmapCMD = bbmap_node_path + "/reformat.sh \
                    -Xmx5g \
                    in1= " + R1 + " \
                    in2= " + R2 + " \
                    out=stdout.sam "

        return shlex.split(bbmapCMD)


