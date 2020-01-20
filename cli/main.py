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

import sys
import logging
import traceback

import click

from cli import __version__
from cli.validator import validator_cli
from cli.utils.validations import UrlType
from cli.utils.helper import safe_mk_dirs, write_json, download_file
from cli.utils.constants import SKALE_VAL_CONFIG_FOLDER, SKALE_VAL_CONFIG_FILE, SKALE_VAL_ABI_FILE

logger = logging.getLogger(__name__)
URL_TYPE = UrlType()


@click.group()
def cli():
    pass


@cli.command('init', help="Set Ethereum endpoint and contracts URL")
@click.option(
    '--endpoint', '-e',
    type=URL_TYPE,
    help='Endpoint of the Ethereum network',
    prompt='Please enter endpoint of the Ethereum network'
)
@click.option(
    '--contracts-url', '-c',
    type=URL_TYPE,
    help='Download URL for the SKALE Manager ABIs and addresses',
    prompt='Please enter URL for the SKALE Manager ABIs and addresses'
)
def init(endpoint, contracts_url):
    safe_mk_dirs(SKALE_VAL_CONFIG_FOLDER)
    download_file(contracts_url, SKALE_VAL_ABI_FILE)
    write_json(SKALE_VAL_CONFIG_FILE, {'endpoint': endpoint})


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception",
                 exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception

if __name__ == '__main__':
    logger.info(f'cmd: {" ".join(str(x) for x in sys.argv)}, v.{__version__}')
    cmd_collection = click.CommandCollection(sources=[cli, validator_cli])
    try:
        cmd_collection()
    except Exception as err:
        print(f'Command execution falied with {err}. Recheck your inputs')
        traceback.print_exc()
        logger.error(err)
