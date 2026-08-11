FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update --fix-missing && apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y  \
                       git \
                       python3.14 \
                       libpython3.14-dev \
                       python3.14-venv \
                       python3.14-dev \
                       build-essential \
                       zlib1g-dev \
                       libssl-dev \
                       libffi-dev \
                       swig

RUN mkdir /app
WORKDIR /app

COPY . .

ENV PATH=/app/buildvenv/bin:$PATH
RUN python3.14 -m venv /app/buildvenv && \
    pip install --upgrade pip && \
    pip install --upgrade wheel 'setuptools>=80.9.0,<81' && \
    pip install -e '.[dev]' 
