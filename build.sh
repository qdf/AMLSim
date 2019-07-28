#!/bin/bash
set -e

TAG=3.9.0.40

if [ "$1" != "" ];
	then TAG=$1
fi

export TAG

#echo $TAG

docker build --build-arg BASE_IMAGE_TAG=$TAG -t docker.quantiply.com:18444/quantiply/amlsim:$TAG .
docker push docker.quantiply.com:18444/quantiply/amlsim:$TAG
docker pull docker.quantiply.com:18443/quantiply/amlsim:$TAG
