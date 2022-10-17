import os
import subprocess
from subprocess import PIPE

from tests.constants import TEST_PK_FILE
from skale.utils.account_tools import generate_account


def test_no_such_command_exit_code(executable):
    cmd = [executable, 'test-shmest']
    result = subprocess.run(cmd, shell=False, stdout=PIPE, stderr=PIPE, env={**os.environ})
    assert result.returncode == 2


def test_reverted_exit_code(skale, executable):
    # generate new address
    addr = generate_account(skale.web3)['address']
    # try to unlink not linked address
    cmd = [
        executable, 'validator', 'unlink-address', addr,
        '--pk-file', TEST_PK_FILE, '--yes'
    ]
    result = subprocess.run(cmd, shell=False, stdout=PIPE, stderr=PIPE, env={**os.environ})
    print(result.stdout, result.returncode)
    assert result.returncode == 6
