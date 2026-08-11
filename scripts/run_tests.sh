#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_DIR=$(dirname $DIR)

export DISABLE_SPIN=True
export SGX_SERVER_URL='https://127.0.0.1:1026'

export SGX_DATA_DIR='tests/tmp-test-sgx'
export ENV=test

bash scripts/run_sgx_simulator.sh

# eth-account registers a legacy Web3 pytest plugin that imports before this
# project's compatibility shim. Load only pytest-cov, which this script needs.
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 py.test -p pytest_cov --cov=$PROJECT_DIR/ $PROJECT_DIR/tests/ --ignore=tests/cli/metrics_node_test.py --ignore=tests/cli/metrics_validator_test.py $@
