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
import urllib
import logging

from utils.constants import SKALE_VAL_CONFIG_FILE, SKALE_VAL_ABI_FILE

logger = logging.getLogger(__name__)


def safe_mk_dirs(path):
    if os.path.exists(path):
        return
    logger.info(f'Creating {path} directory')
    os.makedirs(path, exist_ok=True)


def read_json(path):
    with open(path, encoding='utf-8') as data_file:
        return json.loads(data_file.read())


def write_json(path, content):
    with open(path, 'w') as outfile:
        json.dump(content, outfile, indent=4)


def download_file(url, filepath):
    try:
        return urllib.request.urlretrieve(url, filepath)
    except urllib.error.HTTPError:
        print(f'Couldn\'t donwload file: {url}')


def config_exists():
    return os.path.exists(SKALE_VAL_CONFIG_FILE)


def read_config():
    config = read_json(SKALE_VAL_CONFIG_FILE)
    config['abi'] = read_json(SKALE_VAL_ABI_FILE)
    return config


def get_config():
    if config_exists():
        return read_config()


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()
