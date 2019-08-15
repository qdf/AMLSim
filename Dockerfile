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

RUN scl enable rh-python36 bash && python --version

RUN python --version

RUN sudo curl -fSsL -O https://bootstrap.pypa.io/get-pip.py && \
    sudo python3 get-pip.py && \
    rm get-pip.py

RUN sudo pip3 install \
        numpy==1.14.3 \
        pandas==0.23.0 \
        dill==0.2.7.1 \
        scipy==1.0.0 \
        networkx==1.10 \
        faker==2.0.0 \
        barnum==0.5.1 \
        configparser==3.7.4

#RUN git clone https://github.com/qdf/AMLSim.git

# The user quantiply is created as part of qbase image which is the parent for java8
COPY --chown=quantiply:quantiply . AMLSim

WORKDIR AMLSim

RUN sh scripts/build_AMLSim.sh && \
 sh pipeline.sh
