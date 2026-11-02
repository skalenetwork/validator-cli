#!/usr/bin/env bash
set -e

export DISABLE_SPIN=True
export SGX_SERVER_URL='https://127.0.0.1:1026'
export SGX_DATA_DIR='tests/tmp-test-sgx'

bash scripts/run_sgx_simulator.sh

pytest --cov=cli --cov=core --cov=utils --cov-report=xml tests/ "$@"
