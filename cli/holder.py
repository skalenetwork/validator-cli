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

import click

from utils.texts import Texts
from core.holder import delegate, delegations
from utils.constants import DELEGATION_PERIOD_OPTIONS


G_TEXTS = Texts()
TEXTS = G_TEXTS['holder']


@click.group()
def holder_cli():
    pass


@holder_cli.group('holder', help="Token holder commands")
def holder():
    pass


@holder.command('delegate', help="Delegate tokens to validator")
@click.option(
    '--validator-id',
    type=int,
    help='ID of the validator to delegate',
    prompt='Please enter ID of the validator to delegate'
)
@click.option(
    '--amount',
    type=int,
    help='Amount of SKALE tokens to delegate',
    prompt='Please enter amount of SKALE tokens to delegate'
)
@click.option(
    '--delegation-period',
    type=click.Choice(DELEGATION_PERIOD_OPTIONS),
    help='Delegation period (in months)',
    prompt='Please enter delegation period (in months)'
)
@click.option(
    '--info',
    type=str,
    help='Delegation request info',
    prompt='Please enter delegation request info'
)
@click.option(
    '--pk-file',
    help='File with private key'
)
def _delegate(validator_id, amount, delegation_period, info, pk_file):
    delegate(
        validator_id=validator_id,
        amount=amount,
        delegation_period=delegation_period,
        info=info,
        pk_file=pk_file
    )


@holder.command('delegations', help="List of delegations for address")
@click.argument('address')
def _delegations(address):
    delegations(address)
