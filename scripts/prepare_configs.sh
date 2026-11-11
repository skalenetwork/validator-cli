#!/usr/bin/env bash

set -e

: "${ETH_PRIVATE_KEY?Need to set ETH_PRIVATE_KEY}"

export DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

CLI_CONFIG_FOLDER=$HOME/.skale-val-cli
SGX_FOLDER=$CLI_CONFIG_FOLDER/sgx
CLI_ABI_CONFIG=$CLI_CONFIG_FOLDER/config.json
TEST_PK_FILE=$DIR/../tests/test-pk.txt
if [ -d "$SGX_FOLDER" ]; then
    rm -r "$SGX_FOLDER"
fi

mkdir -p $CLI_CONFIG_FOLDER

ENDPOINT='http://localhost:8545'
MANAGER_CONTRACTS=$(bash $DIR/../helper-scripts/helper.sh manager_address)
echo {\"endpoint\": \"${ENDPOINT}\",\"manager_contracts\": \"${MANAGER_CONTRACTS}\",\"wallet\": \"software\"} > $CLI_ABI_CONFIG
echo $ETH_PRIVATE_KEY > $TEST_PK_FILE
