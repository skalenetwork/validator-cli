""" Tests for cli/main.py module """

import os
import json
import shutil
from distutils.dir_util import copy_tree

from click.testing import CliRunner
from cli import __version__
from cli.info import VERSION
from cli.main import info, init, version
from utils.constants import SKALE_VAL_CONFIG_FOLDER, SKALE_VAL_CONFIG_FILE, SKALE_VAL_ABI_FILE

TMP_CONFIG_FOLDER = '/tmp/.skale-val-config'


def test_info():
    runner = CliRunner()
    result = runner.invoke(info)

    assert result.exit_code == 0
    assert f'Version: {__version__}' in result.output
    assert f'Full version: {VERSION}' in result.output
    assert 'Build time:' in result.output
    assert 'Build OS:' in result.output
    assert 'Commit:' in result.output
    assert 'Git branch:' in result.output
    assert 'unknown' not in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(version)

    assert result.exit_code == 0
    assert result.output == f'{__version__}\n'


def test_init_fail():
    runner = CliRunner()
    result = runner.invoke(
        init,
        ['-e', 'abc']
    )
    assert result.output == 'Usage: init [OPTIONS]\nTry \'init --help\' for help.\n\nError: Invalid value for \'--endpoint\' / \'-e\': Expected valid url. Got abc\n' # noqa


def test_init():
    if os.path.isdir(SKALE_VAL_CONFIG_FOLDER):
        copy_tree(SKALE_VAL_CONFIG_FOLDER, TMP_CONFIG_FOLDER)
        shutil.rmtree(SKALE_VAL_CONFIG_FOLDER)
    assert not os.path.isdir(SKALE_VAL_CONFIG_FOLDER)
    runner = CliRunner()
    result = runner.invoke(
        init,
        ['-e', 'http://example.com/', '-c', 'http://example.com/', '-w', 'software']
    )

    assert os.path.isfile(SKALE_VAL_CONFIG_FILE)
    assert os.path.isfile(SKALE_VAL_ABI_FILE)

    with open(SKALE_VAL_CONFIG_FILE, "r") as f:
        config = json.load(f)
        assert config['wallet'] == 'software'
        assert config['endpoint'] == 'http://example.com/'

    assert result.exit_code == 0
    assert result.output == 'Validator CLI initialized successfully\n'

    if os.path.isdir(TMP_CONFIG_FOLDER):
        copy_tree(TMP_CONFIG_FOLDER, SKALE_VAL_CONFIG_FOLDER)
