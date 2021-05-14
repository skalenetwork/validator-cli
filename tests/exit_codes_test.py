import os
import subprocess
from subprocess import PIPE

from tests.executable_test import get_executable_path
from tests.constants import TEST_PK_FILE


def test_no_such_command_exit_code():
    executable_path = get_executable_path()
    cmd = [executable_path, 'test-shmest']
    result = subprocess.run(cmd, shell=False, stdout=PIPE, stderr=PIPE, env={**os.environ})
    assert result.returncode == 2


def test_reverted_exit_code():
    executable_path = get_executable_path()
    cmd = [
        executable_path, 'validator', 'register', '-n', 'test', '-d', 'test',
        '--commission-rate', '10', '--min-delegation', '1000', '--pk-file', TEST_PK_FILE, '--yes'
    ]
    result = subprocess.run(cmd, shell=False, stdout=PIPE, stderr=PIPE, env={**os.environ})
    assert result.returncode == 6
