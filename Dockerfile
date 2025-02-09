# Build to run entire AMLSim pipeline
# TODO: Make customer and accounts size Parameters

ARG BASE_IMAGE_TAG

FROM docker.quantiply.com:18443/quantiply/java8:${BASE_IMAGE_TAG} as builder

LABEL maintainer="Ryan Compton <compton@quantiply.com>"

RUN sudo yum update -y && sudo yum install -y \
        build-essential \
        curl \
        git \
        git-core \
        java-devel \
        libcurl3-dev \
        pkg-config \
        centos-release-scl \
        rh-python36 \
        rsync \
        software-properties-common \
        unzip \
        zip \
        zlib1g-dev

RUN sudo ln -fs /usr/bin/python3.6 /usr/bin/python && \
   sudo ln -fs /usr/bin/pip3.6 /usr/bin/pip

RUN python --version

RUN sudo curl -fSsL -O https://bootstrap.pypa.io/get-pip.py && \
    sudo python get-pip.py && \
    rm get-pip.py

RUN sudo pip install \
        numpy==1.16.4 \
        pandas==0.25.0 \
        dill==0.3.0 \
        scipy==1.3.0 \
        networkx==2.3 \
        faker==2.0.0 \
        barnum==0.5.1 \
        configparser==3.7.4

#RUN git clone https://github.com/qdf/AMLSim.git

# The user quantiply is created as part of qbase image which is the parent for java8
COPY --chown=quantiply:quantiply . AMLSim

WORKDIR AMLSim

RUN sh scripts/build_AMLSim.sh && \
 sh pipeline.sh
