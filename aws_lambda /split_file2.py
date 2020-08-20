#!/usr/bin/env python3
# coding: utf-8
import boto3
import json 
import time 
import urllib.parse

print("[" + time.strftime('%d-%b-%Y %H:%M:%S', time.localtime()) + "] Loading S3 Files...")
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
def lambda_handler(event, context):
    """
        Handles a S3 bucket trigger event (PUT, POST, COPY) in the reads directory. This function takes care
        of determining fastq file to be a single or paired-read and then sends paired read to the next lambda 
        function.

        s3://flint-implementation/reads/ bucket 
        can only have either unique names or atmost two of the same unique name

        Returns: TODO
    
    """
    reads = []
    keys = []
    r1 = "R1"
    r2 = "R2"
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        print(key)
        #reads/Genome4Test1_1.fastq
        print(type(key))
        # class str 
        if r1 or r2 not in key:
                print("Added file is a single pair read.")
                continue
        elif r1 in key:
            if key.count(r1) > 1:
                print("Critical Error. R1 appears more than once in file_name!")
            read_name = key.split('/')[1].replace("R1","").rstrip(".fastq")
            #Genome4Test1_
            reads.append(read_name)
            keys.append(key)
        else:
            if key.count(r2) > 1:
                print("Critical Error. R2 appears more than once in file_name!")
            read_name = key.split('/')[1].replace("R2","").rstrip(".fastq")
            second_mate = key 
            if len(keys) != 0 and read_name in reads:
                # Find the indice, grab the key and take current key to send_mates to invoke second lambda 
                # function to interleave them 
                index = reads.index(read_name)
                
                # read index should be the same as key index if files are inputting and triggered into s3
                # in consecutive events
                first_mate = keys[index]

                # obj_key gives the full path of the object in s3 bucket 
                obj_key1 = s3_client.get_object(Bucket=bucket, Key=first_mate)
                obj_key2 = s3_client.get_object(Bucket=bucket, Key=second_mate)
                reads.remove(index)
                keys.remove(index)
                send_mates(read_name, obj_key1, obj_key2)
                
                
    print("Records not found. Please debug more.")
    

def send_mates(read_name,obj_key1, obj_key2):
    """
    Returns the two key objects if they are found to be read mates to child lambda function for interleaving
    """
    inputParams = {"ReadName" : read_name, "FirstMate" : obj_key1, "SecondMate" : obj_key2} 
    response = s3_client.invoke(FunctionName= "Interleave",InvocationType='RequestResponse', Payload= json.dumps(inputParams))






def mis():
    s3_object = s3_client.get_object(Bucket=bucket,Key=key)
    # Change text into dictionary
    dict_logs = json.loads(raw_logs)
    # Make sure json_logs key 'Records' exists
    if 'Records' in dict_logs.keys():
        print("Printing Dictionary Content: {} \n\n".format(dict_logs))
        
        # Print Key-Value pair for each item found
        for key, value in dict_logs['Records'][0].items():
            # Account for values that are also dictionaries
            if isinstance(value, dict):
                print("Parent Key: {}".format(key))
                for k, v in value.items():
                    print("Subdict Key: {}".format(k))
                    print("Subdict Value: {}".format(v))
                continue
            else:
                print("Key: {}".format(key))
                print("Value: {}".format(value))
    else: 
        print("Records not found. Please debug more.")


