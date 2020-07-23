#!/usr/bin/python3
# -*- coding: <utf-8> -*-

#Script for troubleshooting streaming fastq inputs to 
#bbmap or bowtie2 aligners [v0.1]
import pyspark
import os, sys
import pickle
from subprocess import Popen, PIPE, STDOUT
import shlex
import pprint as pp
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
fastq = "/home/david/FLINT/Ag10000.IL.fastq"
read1 = "/home/david/FLINT/Ag10000.R1.fastq"
read2 = "/home/david/FLINT/Ag10000.R2.fastq"

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

# remove the interleaved and build line 

def mimicRDD(readfile):
	##In FLINT, RDDs are collected as a list of unicode elements
	##Here, we replicate that structure when inporting a text file
	with open(readfile) as f:
	    reads_list = [line.rstrip() for line in f]
	    reads_list = map(unicode,reads_list)
	return(reads_list)

#Main workflow
#######################################################

sc = pyspark.SparkContext('local[*]')

#txt = sc.textFile('/home/david/FLINT/Ag10000.tab5.txt')
#print(txt.count())

sampleReadsRDD = sc.textFile(fastq)
sample_reads_list = sampleReadsRDD.collect()
#   The RDD with reads is set as a Broadcast variable that will be picked up by each worker node.
broadcast_sample_reads = sc.broadcast(sample_reads_list)
print("Number of reads:{}".format(sample_reads_list))
print("Finished printing....................")
#read file to list of unicode elements (1 element per line)
#reads_list = mimicRDD(tab5)


#reads_list = [line.encode('ascii', errors='ignore') for line in reads_list]
#print(reads_list)

bowtieCMD = getBowtie2Command(bowtie2_index_path=bowtie2_index_path,
                              bowtie2_index_name=bowtie2_index_name,
                              bowtie2_number_threads=bowtie2_number_threads, 
                              bowtie2_filetype=bowtie2_filetype)

bbmapCMD = getBBMAPCommand(bbmap_node_path=bbmap_node_path,
                            bbmap_index_path=bbmap_index_path,
                            bbmap_index_name=bbmap_index_name,
                            bbmap_number_threads=bowtie2_number_threads)

#align_subprocess = Popen(bowtieCMD, stdin=PIPE, stdout=PIPE, stderr=PIPE)
align_subprocess = Popen(bbmapCMD, stdin=PIPE, stdout=PIPE, stderr=PIPE,bufsize=1)

alignment_output, alignment_error = align_subprocess.communicate(input="\n".join(sample_reads_list).encode("latin-1")) #
print("OUTPUT of: alignment_output.strip().decode()\n" + alignment_output.strip().decode())
print("OUTPUT of: alignment_error.strip().decode()\n" + alignment_error.strip().decode())

# # # #   original argument is latin-1
# # # #   The output is returned as a 'bytes' object, so we'll convert it to a list. That way, 'this' worker node
# # # #   will return a list of the alignments it found.
# for a_read in alignment_output.strip().decode().splitlines():
# 	print(a_read)
