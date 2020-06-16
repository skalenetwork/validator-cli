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
from utils.helper import abort_if_false
from core.holder import (delegate, delegations,
                         cancel_pending_delegation, locked,
                         undelegate, withdraw_bounty)
from utils.constants import DELEGATION_PERIOD_OPTIONS


G_TEXTS = Texts()
TEXTS = G_TEXTS['holder']


@click.group()
def holder_cli():
    pass


@holder_cli.group('holder', help=TEXTS['help'])
def holder():
    pass


@holder.command('delegate', help=TEXTS['delegate']['help'])
@click.option(
    '--validator-id',
    type=int,
    help=TEXTS['delegate']['validator_id']['help'],
    prompt=TEXTS['delegate']['validator_id']['prompt']
)
@click.option(
    '--amount',
    type=int,
    help=TEXTS['delegate']['amount']['help'],
    prompt=TEXTS['delegate']['amount']['prompt']
)
@click.option(
    '--delegation-period',
    type=click.Choice(DELEGATION_PERIOD_OPTIONS),
    help=TEXTS['delegate']['delegation_period']['help'],
    prompt=TEXTS['delegate']['delegation_period']['prompt']
)
@click.option(
    '--info',
    type=str,
    help=TEXTS['delegate']['info']['help'],
    prompt=TEXTS['delegate']['info']['prompt']
)
@click.option(
    '--pk-file',
    help=G_TEXTS['pk_file']['help']
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt=TEXTS['delegate']['confirm'])
def _delegate(validator_id, amount, delegation_period, info, pk_file):
    delegate(
        validator_id=validator_id,
        amount=amount,
        delegation_period=int(delegation_period),
        info=info,
        pk_file=pk_file
    )


@holder.command('delegations', help=TEXTS['delegations']['help'])
@click.argument('address')
@click.option('--wei', '-w', is_flag=True, help=TEXTS['delegations']['wei']['help'])
def _delegations(address, wei):
    delegations(address, wei)


@holder.command('cancel-delegation', help=TEXTS['cancel_delegation']['help'])
@click.argument('delegation_id')
@click.option(
    '--pk-file',
    help=G_TEXTS['pk_file']['help']
)
def _cancel_delegation(delegation_id, pk_file):
    cancel_pending_delegation(
        delegation_id=int(delegation_id),
        pk_file=pk_file
    )


@holder.command('undelegate', help=TEXTS['undelegate']['help'])
@click.argument('delegation_id')
@click.option(
    '--pk-file',
    help=G_TEXTS['pk_file']['help']
)
def _undelegate(delegation_id, pk_file):
    undelegate(
        delegation_id=int(delegation_id),
        pk_file=pk_file
    )


@holder.command('withdraw-bounty', help=TEXTS['withdraw_bounty']['help'])
@click.argument('validator_id')
@click.argument('recipient_address')
@click.option(
    '--pk-file',
    help=G_TEXTS['pk_file']['help']
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt=TEXTS['withdraw_bounty']['confirm'])
def _withdraw_bounty(validator_id, recipient_address, pk_file):
    withdraw_bounty(int(validator_id), recipient_address, pk_file)


@holder.command('locked', help=TEXTS['locked']['help'])
@click.argument('address')
@click.option('--wei', '-w', is_flag=True, help=TEXTS['locked']['wei']['help'])
def _locked(address, wei):
    locked(address, wei)
