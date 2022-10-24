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
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import click

from core.srw import recharge, withdraw, balance
from utils.texts import Texts
from utils.helper import transaction_cmd


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
@transaction_cmd
@click.argument('amount')
@click.option(
    '--validator-id',
    type=int,
    help=TEXTS['recharge']['validator_id']['help'],
)
def _recharge(amount, validator_id, pk_file, fee):
    recharge(
        amount=amount,
        validator_id=validator_id,
        pk_file=pk_file,
        fee=fee
    )


@srw.command('withdraw', help=TEXTS['withdraw']['help'])
@transaction_cmd
@click.argument('amount')
def _withdraw(amount, pk_file, fee):
    withdraw(
        amount=amount,
        pk_file=pk_file,
        fee=fee
    )


@srw.command('balance', help=TEXTS['balance']['help'])
@click.option('--wei', '-w', is_flag=True,
              help=G_TEXTS['wei']['help'])
@click.argument('validator_id', type=int)
def _balance(validator_id, wei):
    balance(validator_id, wei)
