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
import sys
from pathlib import Path


def _get_env():
    try:
        sys._MEIPASS
    except AttributeError:
        return 'dev'
    return 'prod'


ENV = _get_env()
CURRENT_FILE_LOCATION = os.path.dirname(os.path.realpath(__file__))

if ENV == 'dev':
    ROOT_DIR = os.path.join(CURRENT_FILE_LOCATION, os.pardir)
else:
    ROOT_DIR = os.path.join(sys._MEIPASS, 'data')

TEXT_FILE = os.path.join(ROOT_DIR, 'text.yml')

LONG_LINE = '-' * 50
SPIN_COLOR = 'yellow'

HOME_DIR = str(Path.home())
SKALE_VAL_CONFIG_FOLDER = os.path.join(HOME_DIR, '.skale-val-cli')
SKALE_VAL_CONFIG_FILE = os.path.join(SKALE_VAL_CONFIG_FOLDER, 'config.json')
SKALE_VAL_ABI_FILE = os.path.join(SKALE_VAL_CONFIG_FOLDER, 'abi.json')

WALLET_TYPES = ['software', 'ledger']
DELEGATION_PERIOD_OPTIONS = ['3', '6', '9', '12']  # strings because of click.Choice design
