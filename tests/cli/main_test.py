#   -*- coding: utf-8 -*-
#
#   This file is part of validator-cli
#
#   Copyright (C) 2020 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import json
import shutil
from distutils.dir_util import copy_tree

from click.testing import CliRunner
from cli.main import init
from utils.constants import SKALE_VAL_CONFIG_FOLDER, SKALE_VAL_CONFIG_FILE, SKALE_VAL_ABI_FILE

TMP_CONFIG_FOLDER = '/tmp/.skale-val-config'


def test_init_fail():
    runner = CliRunner()
    result = runner.invoke(
        init,
        ['-e', 'abc']
    )
    assert result.output == 'Usage: init [OPTIONS]\nTry "init --help" for help.\n\nError: Invalid value for "--endpoint" / "-e": Expected valid url. Got abc\n' # noqa


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
