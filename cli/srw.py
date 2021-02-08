#   -*- coding: utf-8 -*-
#
#   This file is part of validator-cli
#
#   Copyright (C) 2021 SKALE Labs
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

import logging
import click

from core.srw import recharge
from utils.helper import abort_if_false
from utils.texts import Texts


G_TEXTS = Texts()
TEXTS = G_TEXTS['srw']

logger = logging.getLogger(__name__)


@click.group()
def srw_cli():
    pass


@srw_cli.group('srw', help=TEXTS['help'])
def srw():
    pass


@srw.command('recharge', help=TEXTS['recharge']['help'])
@click.argument('amount')
@click.option(
    '--pk-file',
    help=G_TEXTS['pk_file']['help']
)
@click.option(
    '--gas-price',
    type=float,
    help=G_TEXTS['gas_price']['help']
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False, prompt=G_TEXTS['yes_opt']['prompt'])
def _recharge(amount, pk_file, gas_price):
    recharge(amount, pk_file, gas_price)
