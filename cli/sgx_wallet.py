#   -*- coding: utf-8 -*-
#
#   This file is part of skale-node-cli
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
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json

import click

from core.sgx_tools import init_sgx_account, get_sgx_info, sgx_inited
from utils.print_formatters import print_sgx_info
from utils.texts import Texts


G_TEXTS = Texts()
TEXTS = G_TEXTS['sgx']
MSGS = G_TEXTS['msg']


@click.group()
def sgx_cli():
    pass


@sgx_cli.group('sgx', help=TEXTS['help'])
def sgx_wallet():
    pass


@sgx_wallet.command(help=TEXTS['init']['help'])
@click.argument('sgx-url')
@click.option('--force', '-f', is_flag=True)
@click.option('--ssl-port', help=TEXTS['init']['param']['ssl_port'], type=int,
              default=1026)
def init(sgx_url, force, ssl_port):
    if not force and sgx_inited():
        print(TEXTS['init']['msg']['already_inited'])
        return

    info = init_sgx_account(sgx_url, ssl_port)
    print(TEXTS['init']['msg']['success'])
    print_sgx_info(info)
    print(TEXTS['init']['msg']['warning'])


@sgx_wallet.command(help=TEXTS['info']['help'])
@click.option('--raw', is_flag=True)
def info(raw):
    if not sgx_inited():
        print('SGX is not inited')
    else:
        info = get_sgx_info()
        if raw:
            print(json.dumps(info))
        else:
            print_sgx_info(info)
