#!/usr/bin/env bash

set -e

SGX_WALLET_TAG=${SGX_WALLET_TAG:-develop-latest}
SGX_WALLET_IMAGE_NAME=skalenetwork/sgxwallet_sim:$SGX_WALLET_TAG
SGX_WALLET_CONTAINER_NAME=sgx_simulator

echo Going to run $SGX_WALLET_IMAGE_NAME ...

docker rm -f $SGX_WALLET_CONTAINER_NAME || true
docker pull $SGX_WALLET_IMAGE_NAME
docker run -d --network host --name $SGX_WALLET_CONTAINER_NAME $SGX_WALLET_IMAGE_NAME -s -y -d -e
sleep 5
