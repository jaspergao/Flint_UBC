#!/usr/bin/env python
# -*- coding: <utf-8> -*-

#Script for troubleshooting streaming fastq inputs to 
#bbmap or bowtie2 aligners [v0.1]
import pyspark
import os, sys
import pickle
from subprocess import Popen, PIPE, STDOUT
import shlex
import pprint as pp
import timeit 
# #Lambda functions 
# x = ['Python', 'programming', 'is', 'awesome!']
# print(sorted(x, key=lambda arg: arg.lower()))
# print(list(filter(lambda arg: len(arg) < 8, x)))
#Read text file to list of unicode elements
#Pipe elements to bowtie2
#NOTE: Bowtie2 <=2.3.5 does not work with interleaved fastq 
#Upgrade to 2.4.1 
# BBMap v38.86

#Define variables
#######################################################
fastq = "/home/david/FLINT/Ag10000.IL.fastq"  #interleaved 
read_sub8_1 = "/home/jasper/forward_reads/Ag8.R1.fastq" #forward
read_sub8_2 = "/home/jasper/reverse_reads/Ag8.R2.fastq" #reverse

#read1 = "/home/david/FLINT/Ag10000.R1.fastq"
#read2 = "/home/david/FLINT/Ag10000.R2.fastq"

read1 = "/home/jasper/forward_reads/Ag100_Il_R1.fastq"
read2 = "/home/jasper/forward_reads/Ag100_Il_R2.fastq"

#class tab5():
tab5 = "/home/david/FLINT/Ag10000.tab5.txt" 

#bowtie2
bowtie2_index_path = "/home/david/FLINT/1"
bowtie2_index_name = "assemble"
bowtie2_number_threads = 6
bowtie2_filetype = "tab5"

#bbmap
bbmap_index_path = "/home/jasper/"
bbmap_index_name = "1"
bbmap_number_threads = 6
bbmap_node_path = "/home/david/bbmap"

#Define functions
#######################################################
def checkIllumnia(r1_RDD, r2RDD):
    # gives a list of just the IDs of each RDD 
    r1_name_list = r1_RDD[::4]
    r2_name_list = r2_RDD[::4]

    # set flag to be False initially 
    illumnia = False

    # O(n^2) complexity looping through both lists to check if the first item
    # in split is the same as the first item in second read split
    # if True; change bool flag to True
    for r1 in r1_name_list:
        for r2 in r2_name_list:
            if r1.split()[0] == r2.split()[0]:
                illumnia = True 

    return illumnia 


# method 1 to merge list
def merge_list(r1_RDD, r2_RDD):
    sep = 4
    num = len(r1_RDD)
    iterations = int(num / sep) + 1

    merged = []
    for i in range(iterations):
        start = sep * i
        end = sep * (i + 1)
        merged.extend(r1_RDD[start:end])
        merged.extend(r2_RDD[start:end])
    return merged

# method 2 to merge list
def merge_list2(r1_RDD, r2_RDD):
    l=[]
    for i in range(0,len(r1_RDD),4):
        l.extend(r1_RDD[i:i+4])
        l.extend(r2_RDD[i:i+4])
    return l

def getBowtie2Command(bowtie2_index_path, bowtie2_index_name, bowtie2_number_threads, bowtie2_filetype):
    index_location  = bowtie2_index_path
    index_name      = bowtie2_index_name
    index = index_location + "/" + index_name
    number_of_threads = bowtie2_number_threads
    filetype = bowtie2_filetype.lower()
    
    if filetype not in ["tab5", "fastq"]:
        raise Exception("Filetype: {} not supported. Please enter either tab5 or fastq".format(filetype))
    if filetype == "tab5":
 	    bowtieCMD = "bowtie2 \
 	                --threads " + str(number_of_threads) + " \
 	                --local \
 	                -D 20 \
	                -R 3 \
 	                -N 0 \
 	                -L 20 \
 	                --no-sq \
 	                --no-hd \
 	                --no-unal \
 	                -q \
 	                -x " + index + " --tab5 -"

    if filetype == "fastq":
         bowtieCMD = "bowtie2 \
                 --threads " + str(number_of_threads) + " \
                 --no-sq \
                 --no-hd \
                 --no-unal \
                 -q \
                 -x " + index + " \
                 --interleaved -"

    return shlex.split(bowtieCMD)

def getBBMAPCommand(bbmap_node_path,bbmap_index_path, bbmap_index_name, bbmap_number_threads):
    index_location  = bbmap_index_path
    index_name      = bbmap_index_name
    index = index_location + "/" + index_name
    number_of_threads = bbmap_number_threads
    
    bbmapCMD = bbmap_node_path + "/bbmap.sh path={} build={} t={}\
                 in=stdin.fq \
                 outm=stdout.sam \
                 minidentity=0.97 \
                 interleaved=t \
                 noheader=t".format(index_location, index_name, number_of_threads)

    return shlex.split(bbmapCMD)


# PySpark TextFile Workflow small file 8 lines 2 reads
#----------------------------------------------------------
sc = pyspark.SparkContext('local[*]')
r1_read = sc.textFile(read1)
r2_read = sc.textFile(read2)

r1_RDD = r1_read.collect()
print(type(r1_RDD))
print("Contents of forward:{}".format(r1_RDD))
r2_RDD = r2_read.collect()
print("Contents of reverse:{}".format(r2_RDD))

print(len(r1_RDD))
print(len(r2_RDD))

illumnia_flag = checkIllumnia(r1_RDD,r2_RDD)

# method 1 
# @chrom... identifyier is not the same so cannot use it as a key but rather just values. Key will be the index

if illumnia_flag:
    interleave_list = merge_list(r1_RDD,r2_RDD)
    print("Contents of interleave:{}".format(interleave_list))
    interleave_list_2 = merge_list2(r1_RDD,r2_RDD)
    print("Contents of interleave_2:{}".format(interleave_list))

    print("---------------------------")
    print("interleave length is:{}".format(len(interleave_list)))
    print("---------------------------")
    print("interleave_2 length is:{}".format(len(interleave_list_2)))   


    broadcast_sample_reads = sc.broadcast(interleave_list_2)
    # refactor to include illumnia flag
    bbmapCMD = getBBMAPCommand(bbmap_node_path=bbmap_node_path,
                            bbmap_index_path=bbmap_index_path,
                            bbmap_index_name=bbmap_index_name,
                            bbmap_number_threads=bowtie2_number_threads)

    align_subprocess = Popen(bbmapCMD, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)

    alignment_output, alignment_error = align_subprocess.communicate(input="\n".join(interleave_list).encode('latin-1')) #
    print("OUTPUT of: alignment_output.strip().decode()\n" + alignment_output.strip().decode())
    print("OUTPUT of: alignment_error.strip().decode()\n" + alignment_error.strip().decode())
else:
    raise Exception("File is not in Illumnia format and is not supported. Please enter Illumnia consistent fastq")

#intereave_RDD = sc.parallelize(interleave_list)
# since we have 64 nodes we are creating a new empty RDD with partition size
#data = sc.parallelize(range(1, partition_size))
#data_num_partitions = data.getNumPartitions()

# remove the interleaved and build line 
