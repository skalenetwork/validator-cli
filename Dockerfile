FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update --fix-missing && apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y  \
                       git \
                       python3.9 \
                       libpython3.9-dev \
                       python3.9-venv \
                       python3.9-distutils \
                       python3.9-dev \
                       build-essential \
                       zlib1g-dev \
                       libssl-dev \
                       libffi-dev \
                       swig

RUN mkdir /app
WORKDIR /app

COPY . .

ENV PATH=/app/buildvenv/bin:$PATH
RUN python3.9 -m venv /app/buildvenv && \
    pip install --upgrade pip && \
    pip install wheel setuptools==63.2.0 && \
    pip install -e '.[dev]' 
