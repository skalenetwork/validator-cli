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
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import click

from core.wallet import send_eth, send_skl, setup_ledger
from utils.helper import abort_if_false
from utils.texts import Texts
from utils.constants import LEDGER_KEYS_TYPES

G_TEXTS = Texts()
TEXTS = G_TEXTS['wallet']

logger = logging.getLogger(__name__)


@click.group()
def wallet_cli():
    pass


@wallet_cli.group('wallet', help=TEXTS['help'])
def wallet():
    pass


@wallet.command('send-eth', help=TEXTS['send_eth']['help'])
@click.argument('receiver_address')
@click.argument('amount')
@click.option(
    '--pk-file',
    help=G_TEXTS['pk_file']['help']
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False, prompt=TEXTS['send_eth']['confirm'])
def _send_eth(receiver_address, amount, pk_file):
    send_eth(receiver_address, amount, pk_file)


@wallet.command('send-skl', help=TEXTS['send_skl']['help'])
@click.argument('receiver_address')
@click.argument('amount')
@click.option(
    '--pk-file',
    help=G_TEXTS['pk_file']['help']
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False, prompt=TEXTS['send_skl']['confirm'])
def _send_skl(receiver_address, amount, pk_file):
    send_skl(receiver_address, amount, pk_file)


@wallet.command('setup-ledger', help=TEXTS['setup_ledger']['help'])
@click.option(
    '--address-index',
    type=int,
    help=G_TEXTS['address_index']['help'],
    prompt=G_TEXTS['address_index']['prompt']
)
@click.option(
    '--keys-type',
    type=click.Choice(LEDGER_KEYS_TYPES),
    help=TEXTS['setup_ledger']['keys_type']['help'],
    prompt=TEXTS['setup_ledger']['keys_type']['prompt']
)
def _setup_ledger(address_index, keys_type):
    setup_ledger(address_index, keys_type)
