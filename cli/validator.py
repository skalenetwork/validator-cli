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

from yaspin import yaspin
from skale.utils.web3_utils import wait_receipt, check_receipt

from cli.utils.helper import read_config, config_exists, abort_if_false
from cli.utils.validations import EthAddressType, PercentageType, UrlType
from cli.utils.web3_utils import init_skale
from cli.utils.constants import LONG_LINE, SKALE_VAL_ABI_FILE


ETH_ADDRESS_TYPE = EthAddressType()
PERCENTAGE_TYPE = PercentageType()
URL_TYPE = UrlType()


@click.group()
def validator_cli():
    pass


@validator_cli.command('register', help="Register new SKALE validator")
@click.option(
    '--name', '-n',
    type=str,
    help='Validator name',
    prompt='Please enter validator name'
)
# @click.option(
#     '--address', '-a',
#     type=ETH_ADDRESS_TYPE,
#     help='Validator address',
#     prompt='Please enter validator address'
# )
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
    '--private-key', '-p',
    help='Validator\'s private key',
    prompt='Enter validator\'s private key'
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt=f'{LONG_LINE}\nAre you sure you want to register a new validator account? \
                  \nPlease, re-check all values above before confirming.')
def register(name, description, commission_rate, min_delegation, private_key):
    if config_exists():
        config = read_config()
    else:
        print('You should run < init > first')
        return
    skale = init_skale(config['endpoint'], SKALE_VAL_ABI_FILE, private_key)
    with yaspin(text="Loading", color="yellow") as sp:
        sp.text = 'Registering new validator'
        tx_res = skale.delegation_service.register_validator(
            name=name,
            description=description,
            fee_rate=int(commission_rate),
            min_delegation_amount=int(min_delegation)
        )
        receipt = wait_receipt(skale.web3, tx_res.hash)
        if check_receipt(receipt):
            sp.write("✔ New validator registered")
