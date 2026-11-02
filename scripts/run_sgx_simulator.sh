#!/usr/bin/env bash

set -e

: "${SGX_WALLET_TAG?Need to set SGX_WALLET_TAG}"
SGX_WALLET_CONTAINER_NAME=sgx_simulator

docker rm -f $SGX_WALLET_CONTAINER_NAME || true
docker run -d -p 1026-1031:1026-1031 --name $SGX_WALLET_CONTAINER_NAME --entrypoint /bin/bash \
    ghcr.io/skalenetwork/sgxwallet_sim:$SGX_WALLET_TAG \
    -c "source /opt/intel/sgxsdk/environment && cd /usr/src/sdk && ./sgxwallet -s -y"
timeout 300 bash -c 'until (echo > /dev/tcp/127.0.0.1/1026) 2>/dev/null; do sleep 1; done'
