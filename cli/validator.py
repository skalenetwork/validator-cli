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

from core.validator import (register, validators_list, delegations, accept_pending_delegation,
                            link_node_address, unlink_node_address, linked_addresses, info)
from utils.helper import abort_if_false
from utils.validations import EthAddressType, PercentageType, UrlType
from utils.constants import LONG_LINE
from utils.texts import Texts


ETH_ADDRESS_TYPE = EthAddressType()
PERCENTAGE_TYPE = PercentageType()
URL_TYPE = UrlType()

G_TEXTS = Texts()
TEXTS = G_TEXTS['validator']


@click.group()
def validator_cli():
    pass


@validator_cli.group('validator', help="Validator commands")
def validator():
    pass


@validator.command('register', help="Register new SKALE validator")
@click.option(
    '--name', '-n',
    type=str,
    help='Validator name',
    prompt='Please enter validator name'
)
@click.option(
    '--description', '-d',
    type=str,
    help='Validator description',
    prompt='Please enter validator description'
)
@click.option(
    '--commission-rate', '-c',
    type=PERCENTAGE_TYPE,
    help='Commission rate (percentage)',
    prompt='Please enter validator commission rate (in percents)'
)
@click.option(
    '--min-delegation',
    type=int,
    help='Validator minimum delegation amount',
    prompt='Please enter minimum delegation amount'
)
@click.option(
    '--pk-file',
    help='File with validator\'s private key'
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt=f'{LONG_LINE}\nAre you sure you want to register a new validator account? \
                  \nPlease, re-check all values above before confirming.')
def _register(name, description, commission_rate, min_delegation, pk_file):
    register(
        name=name,
        description=description,
        commission_rate=int(commission_rate),
        min_delegation=int(min_delegation),
        pk_file=pk_file
    )


@validator.command('ls', help=TEXTS['ls']['help'])
def _ls():
    validators_list()


@validator.command('delegations', help=TEXTS['delegations']['help'])
@click.argument('address')
def _delegations(address):
    delegations(address)


@validator.command('accept-delegation', help=TEXTS['accept_delegation']['help'])
@click.option(
    '--delegation-id',
    type=int,
    help=TEXTS['accept_delegation']['delegation_id']['help'],
    prompt=TEXTS['accept_delegation']['delegation_id']['prompt']
)
@click.option(
    '--pk-file',
    help=TEXTS['accept_delegation']['pk_file']['help']
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
@click.option(
    '--pk-file',
    help=TEXTS['link_address']['pk_file']['help']
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt=TEXTS['link_address']['confirm'])
def _link_address(node_address, pk_file):
    link_node_address(node_address, pk_file)


@validator.command('unlink-address', help=TEXTS['unlink_address']['help'])
@click.argument('node_address')
@click.option(
    '--pk-file',
    help=TEXTS['unlink_address']['pk_file']['help']
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
