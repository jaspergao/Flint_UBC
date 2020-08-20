#!/bin/bash

#	Exit immediately if a command exits with a non-zero exit status. -x verbose bash workflow
set -e -x

aws s3 sync s3://flint-implementation/flint-master /home/hadoop


echo "[" `date '+%m/%d/%y %H:%M:%S'` "] Attempting to change permissions....."
chmod -R 755 /home/hadoop
echo "[" `date '+%m/%d/%y %H:%M:%S'` "] Permissions Changed....."
echo $PWD 
# enter the home directory 
cd /home/hadoop
mkdir reads
echo "[" `date '+%m/%d/%y %H:%M:%S'` "] Created reads directory"
cd reads
echo $PWD
mkdir interleave
echo "[" `date '+%m/%d/%y %H:%M:%S'` "] Created interleave directory"
mkdir single_reads
echo "[" `date '+%m/%d/%y %H:%M:%S'` "] Created single_reads directory"
