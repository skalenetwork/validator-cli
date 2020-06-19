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

import click
from web3 import Web3

from core.validator import (register, validators_list, delegations, accept_pending_delegation,
                            get_bond_amount, link_node_address, unlink_node_address,
                            linked_addresses, info,
                            withdraw_fee)
from utils.helper import abort_if_false
from utils.validations import EthAddressType, UrlType, FloatPercentageType
from utils.texts import Texts


ETH_ADDRESS_TYPE = EthAddressType()
FLOAT_PERCENTAGE_TYPE = FloatPercentageType()
URL_TYPE = UrlType()

G_TEXTS = Texts()
TEXTS = G_TEXTS['validator']


@click.group()
def validator_cli():
    pass


@validator_cli.group('validator', help="Validator commands")
def validator():
    pass


@validator.command('register', help=TEXTS['register']['help'])
@click.option(
    '--name', '-n',
    type=str,
    help=TEXTS['register']['name']['help'],
    prompt=TEXTS['register']['name']['prompt']
)
@click.option(
    '--description', '-d',
    type=str,
    help=TEXTS['register']['description']['help'],
    prompt=TEXTS['register']['description']['prompt']
)
@click.option(
    '--commission-rate', '-c',
    type=FLOAT_PERCENTAGE_TYPE,
    help=TEXTS['register']['commission_rate']['help'],
    prompt=TEXTS['register']['commission_rate']['prompt']
)
@click.option(
    '--min-delegation',
    type=int,
    help=TEXTS['register']['min_delegation']['help'],
    prompt=TEXTS['register']['min_delegation']['prompt']
)
@click.option(
    '--pk-file',
    help=G_TEXTS['pk_file']['help']
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False, prompt=TEXTS['register']['confirm'])
def _register(name, description, commission_rate, min_delegation, pk_file):
    register(
        name=name,
        description=description,
        commission_rate=float(commission_rate),
        min_delegation=int(min_delegation),
        pk_file=pk_file
    )


@validator.command('ls', help=TEXTS['ls']['help'])
@click.option('--wei', '-w', is_flag=True, help=TEXTS['ls']['wei']['help'])
@click.option('--all', is_flag=True)
def _ls(wei, all):
    validators_list(wei, all)


@validator.command('delegations', help=TEXTS['delegations']['help'])
@click.argument('validator_id')
@click.option('--wei', '-w', is_flag=True, help=TEXTS['delegations']['wei']['help'])
def _delegations(validator_id, wei):
    delegations(validator_id, wei)


@validator.command('accept-delegation', help=TEXTS['accept_delegation']['help'])
@click.option(
    '--delegation-id',
    type=int,
    help=TEXTS['accept_delegation']['delegation_id']['help'],
    prompt=TEXTS['accept_delegation']['delegation_id']['prompt']
)
@click.option(
    '--pk-file',
    help=G_TEXTS['pk_file']['help']
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt=TEXTS['accept_delegation']['confirm'])
def _accept_delegation(delegation_id, pk_file):
    accept_pending_delegation(
        delegation_id=int(delegation_id),
        pk_file=pk_file
    )


@validator.command('link-address', help=TEXTS['link_address']['help'])
@click.argument('node_address')
@click.argument('signature')
@click.option(
    '--pk-file',
    help=G_TEXTS['pk_file']['help']
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt=TEXTS['link_address']['confirm'])
def _link_address(node_address, signature, pk_file):
    node_address = Web3.toChecksumAddress(node_address)
    link_node_address(node_address, signature, pk_file)


@validator.command('unlink-address', help=TEXTS['unlink_address']['help'])
@click.argument('node_address')
@click.option(
    '--pk-file',
    help=G_TEXTS['pk_file']['help']
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt=TEXTS['unlink_address']['confirm'])
def _unlink_address(node_address, pk_file):
    unlink_node_address(node_address, pk_file)


@validator.command('linked-addresses', help=TEXTS['linked_addresses']['help'])
@click.argument('address')
def _linked_addresses(address):
    linked_addresses(address)


@validator.command('info', help=TEXTS['info']['help'])
@click.argument('validator_id')
def _info(validator_id):
    info(
        validator_id=int(validator_id)
    )


@validator.command('withdraw-fee', help=TEXTS['withdraw_fee']['help'])
@click.argument('recipient_address')
@click.option(
    '--pk-file',
    help=G_TEXTS['pk_file']['help']
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt=TEXTS['withdraw_fee']['confirm'])
def _withdraw_fee(recipient_address, pk_file):
    withdraw_fee(recipient_address, pk_file)


@validator.command('bond-amount', help=TEXTS['bond_amount']['help'])
@click.option('--wei', '-w', is_flag=True,
              help=TEXTS['bond_amount']['wei']['help'])
@click.argument('validator_id', type=int)
def _bond_amount(validator_id, wei):
    get_bond_amount(validator_id, wei)
