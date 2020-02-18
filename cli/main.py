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

import sys
import logging
import inspect
import traceback

import click

from cli import __version__
from cli.info import BUILD_DATETIME, COMMIT, BRANCH, OS, VERSION
from cli.validator import validator_cli
from cli.holder import holder_cli
from utils.validations import UrlType
from utils.texts import Texts
from utils.helper import safe_mk_dirs, write_json, download_file
from utils.constants import (SKALE_VAL_CONFIG_FOLDER, SKALE_VAL_CONFIG_FILE,
                             SKALE_VAL_ABI_FILE, LONG_LINE, WALLET_TYPES)


logger = logging.getLogger(__name__)
URL_TYPE = UrlType()
TEXTS = Texts()


@click.group()
def cli():
    pass


@cli.command('info', help=TEXTS['info']['help'])
def info():
    print(inspect.cleandoc(f'''
            {LONG_LINE}
            Version: {__version__}
            Full version: {VERSION}
            Build time: {BUILD_DATETIME}
            Build OS: {OS}
            Commit: {COMMIT}
            Git branch: {BRANCH}
            {LONG_LINE}
        '''))


@cli.command('init', help=TEXTS['init']['help'])
@click.option(
    '--endpoint', '-e',
    type=URL_TYPE,
    help=TEXTS['init']['endpoint']['help'],
    prompt=TEXTS['init']['endpoint']['prompt']
)
@click.option(
    '--contracts-url', '-c',
    type=URL_TYPE,
    help=TEXTS['init']['contracts_url']['help'],
    prompt=TEXTS['init']['contracts_url']['prompt']
)
@click.option(
    '--wallet', '-w',
    type=click.Choice(WALLET_TYPES),
    help=TEXTS['init']['wallet']['help'],
    prompt=TEXTS['init']['wallet']['prompt']
)
def init(endpoint, contracts_url, wallet):
    safe_mk_dirs(SKALE_VAL_CONFIG_FOLDER)
    download_file(contracts_url, SKALE_VAL_ABI_FILE)
    config = {
        'endpoint': endpoint,
        'wallet': wallet
    }
    write_json(SKALE_VAL_CONFIG_FILE, config)
    print(TEXTS['init']['done'])


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception",
                 exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception

if __name__ == '__main__':
    logger.info(f'cmd: {" ".join(str(x) for x in sys.argv)}, v.{__version__}')
    cmd_collection = click.CommandCollection(sources=[cli, validator_cli, holder_cli])
    try:
        cmd_collection()
    except Exception as err:
        print(f'Command execution failed with {err}. Recheck your inputs')
        traceback.print_exc()
        logger.error(err)
