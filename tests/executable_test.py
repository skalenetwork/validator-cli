import os
import subprocess
from subprocess import PIPE

from tests.constants import DIST_DIR


def get_executable_name():
    return os.listdir(DIST_DIR)[0]


def get_executable_path():
    return os.path.join(DIST_DIR, get_executable_name())


def test_init(runner):
    executable_path = get_executable_path()
    cmd = [executable_path, 'info']
    result = subprocess.run(cmd, shell=False, stdout=PIPE, stderr=PIPE, env={**os.environ})
    print(f'STDOUT: {result.stdout}')
    assert 'Full version: 0.0.0' in str(result.stdout)
    assert result.stderr == b''
    assert result.returncode == 0
