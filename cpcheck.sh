#!/bin/bash

echo "## checkpoint secure check system. v1.0.1 ##"
# licese: GPLv2
echo "## usage: ./checkpoint {args}, args: times of spark process which has been started. ##"
echo "## This script must be runned at checkpoint directory. ##"

if test -z "$1"
then
    echo "arg is null, please restart script like this: ./checkpoint 1"
    exit 2
fi

sleep 2
echo "checking..."

while [ 1 ]
do
    counter=`ls -l | grep "^d" | wc -l`
    counter=`expr $counter + 0`
    cpnum=`expr $1 + 1`
    if [[ ("$counter" = "$cpnum") ]];then
        sleep 1
    else
        echo "WARNING: checkpoint maybe has been hacked!"
    fi

    sleep 2
done;
