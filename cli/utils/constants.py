#   -*- coding: utf-8 -*-
#
#   This file is part of skale-node-cli
#
#   Copyright (C) 2019 SKALE Labs
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
from pathlib import Path

LONG_LINE = '-' * 50

HOME_DIR = str(Path.home())
SKALE_VAL_CONFIG_FOLDER = os.path.join(HOME_DIR, '.skale-val-cli')
SKALE_VAL_CONFIG_FILE = os.path.join(SKALE_VAL_CONFIG_FOLDER, 'config.json')
SKALE_VAL_ABI_FILE = os.path.join(SKALE_VAL_CONFIG_FOLDER, 'abi.json')
