#!/usr/bin/env bash

if [[ $# -ne 2 ]]; then
    echo "Usage: sh $0 [SimulationName] [Steps]"
    exit 1
fi

MIN_HEAP=2g
MAX_HEAP=30g

NAME=$1
STEP=$2

java -XX:+UseConcMarkSweepGC -XX:ParallelGCThreads=2 -Xms${MIN_HEAP} -Xmx${MIN_HEAP} -cp "jars/*:bin" amlsim.AMLSim -file amlsim.properties -for ${STEP} -r 1 -name ${NAME}
