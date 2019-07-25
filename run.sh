#!/bin/bash
set -e

TAG=3.9.0.40

if [ "$1" != "" ];
	then TAG=$1
fi

export TAG

#echo $TAG
docker run -it --rm --name amlsim \
	--mount type=bind,source=$HOME/AMLSim,target=/home/quantiply/AMLSim/outputs/cust_acct_tx_generation \
	docker.quantiply.com:18443/quantiply/amlsim:$TAG bash