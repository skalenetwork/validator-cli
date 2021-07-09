#   -*- coding: utf-8 -*-
#
#   This file is part of validator-cli
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

import sys

import click
from yaspin import yaspin
from terminaltables import SingleTable

from utils.web3_utils import (init_skale_from_config, init_skale_w_wallet_from_config)
from utils.print_formatters import (print_bond_amount, print_validators,
                                    print_delegations, print_linked_addresses)
from utils.helper import to_wei, from_wei, percent_to_permille, permille_to_percent, print_gas_price
from utils.constants import SPIN_COLOR


def register(name: str, description: str, commission_rate: float, min_delegation: int,
             pk_file: str, gas_price: int) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    if gas_price is None:
        gas_price = skale.gas_price
        print_gas_price(gas_price)
    with yaspin(text='Registering new validator', color=SPIN_COLOR) as sp:
        min_delegation_wei = to_wei(min_delegation)
        commission_rate_permille = percent_to_permille(commission_rate)
        tx_res = skale.validator_service.register_validator(
            name=name,
            description=description,
            fee_rate=commission_rate_permille,
            min_delegation_amount=min_delegation_wei,
            wait_for=True,
            gas_price=gas_price
        )
        sp.write("✔ New validator registered")
        print(f'Transaction hash: {tx_res.tx_hash}')


def validators_list(wei, all):
    skale = init_skale_from_config()
    if not all:
        validators = skale.validator_service.ls(trusted_only=True)
    else:
        validators = skale.validator_service.ls()
    print_validators(validators, wei)


def delegations(validator_id, wei):
    skale = init_skale_from_config()
    if not skale:
        return
    delegations_list = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id)
    print(f'Delegations for validator ID {validator_id}:\n')
    print_delegations(delegations_list, wei)


def accept_pending_delegation(delegation_id, pk_file: str, gas_price: int) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    if gas_price is None:
        gas_price = skale.gas_price
        print_gas_price(gas_price)
    with yaspin(text='Accepting delegation request', color=SPIN_COLOR) as sp:
        tx_res = skale.delegation_controller.accept_pending_delegation(
            delegation_id=delegation_id,
            wait_for=True,
            gas_price=gas_price
        )
        sp.write(f'✔ Delegation request with ID {delegation_id} accepted')
        print(f'Transaction hash: {tx_res.tx_hash}')


def accept_all_delegations(pk_file: str, gas_price: int) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    if gas_price is None:
        gas_price = skale.gas_price
        print_gas_price(gas_price)
    validator_id = skale.validator_service.validator_id_by_address(skale.wallet.address)
    delegations_list = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id)

    pending_delegations = list(filter(lambda delegation: delegation['status'] == 'PROPOSED',
                                      delegations_list))
    n_of_pending_delegations = len(pending_delegations)
    if n_of_pending_delegations == 0:
        print('No pending delegations to accept')
        return

    print(f'\n{n_of_pending_delegations} delegation(s) will be accepted:\n')
    print_delegations(pending_delegations, False)

    if not click.confirm('\nDo you want to continue?'):
        print('Operation canceled')
        return

    with yaspin(text='Accepting ALL delegation requests', color=SPIN_COLOR) as sp:
        for delegation in pending_delegations:
            tx_res = skale.delegation_controller.accept_pending_delegation(
                delegation_id=delegation['id'],
                wait_for=True,
                gas_price=gas_price
            )
            sp.write(f'✔ Delegation request with ID {delegation["id"]} accepted')
            print(f'Transaction hash: {tx_res.tx_hash}')


def link_node_address(node_address: str, signature: str, pk_file: str,
                      gas_price: int) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    if gas_price is None:
        gas_price = skale.gas_price
        print_gas_price(gas_price)
    with yaspin(text='Linking node address', color=SPIN_COLOR) as sp:
        tx_res = skale.validator_service.link_node_address(
            node_address=node_address,
            signature=signature,
            wait_for=True,
            gas_price=gas_price
        )
        sp.write(f'✔ Node address {node_address} linked to your validator address')
        print(f'Transaction hash: {tx_res.tx_hash}')


def unlink_node_address(node_address: str, pk_file: str, gas_price: int) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    if gas_price is None:
        gas_price = skale.gas_price
        print_gas_price(gas_price)
    with yaspin(text='Unlinking node address', color=SPIN_COLOR) as sp:
        tx_res = skale.validator_service.unlink_node_address(
            node_address=node_address,
            wait_for=True,
            gas_price=gas_price
        )
        sp.write(f'✔ Node address {node_address} unlinked from your validator address')
        print(f'Transaction hash: {tx_res.tx_hash}')


def linked_addresses(address):
    skale = init_skale_from_config()
    if not skale:
        return
    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        address)
    addresses_info = get_addresses_info(skale, addresses)
    print(f'Linked addresses for {address}:\n')
    print_linked_addresses(addresses_info)


def get_addresses_info(skale, addresses):
    return [
        {
            'address': address,
            'status': 'Primary' if skale.validator_service.is_main_address(address) else 'Linked',
            'balance': str(skale.web3.fromWei(skale.web3.eth.getBalance(address), 'ether'))
        }
        for address in addresses
    ]


def info(validator_id):
    skale = init_skale_from_config()
    if not skale:
        return
    validator_info = skale.validator_service.get(validator_id)
    # is_accepting_new_requests = skale.validator_service.is_accepting_new_requests(validator_id)
    # accepting_delegation_requests = 'Yes' if is_accepting_new_requests else 'No'
    minimum_delegation_amount = from_wei(
        validator_info['minimum_delegation_amount'])
    fee_rate_percent = permille_to_percent(validator_info['fee_rate'])
    table = SingleTable([
        ['Validator ID', validator_id],
        ['Name', validator_info['name']],
        ['Address', validator_info['validator_address']],
        ['Fee rate (percent %)', fee_rate_percent],
        ['Minimum delegation amount (SKL)', minimum_delegation_amount]
        # ['Auto accept', validator_info['auto_accept_delegations']],
        # ['Accepting delegation requests', accepting_delegation_requests]
    ])
    print(table.table)


def withdraw_fee(recipient_address: str, pk_file: str, gas_price: int) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    if gas_price is None:
        gas_price = skale.gas_price
        print_gas_price(gas_price)
    with yaspin(text='Withdrawing fee', color=SPIN_COLOR) as sp:
        tx_res = skale.distributor.withdraw_fee(
            to=recipient_address,
            wait_for=True,
            gas_price=gas_price
        )
        sp.write(f'✔ Earned fees successfully transferred to {recipient_address}')
        print(f'Transaction hash: {tx_res.tx_hash}')


def get_bond_amount(validator_id, wei=False):
    skale = init_skale_from_config()
    bond_amount = skale.validator_service.get_and_update_bond_amount(
        validator_id
    )
    print_bond_amount(validator_id, bond_amount, wei)


def set_mda(new_mda: int, pk_file: str, gas_price: int) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    if gas_price is None:
        gas_price = skale.gas_price
        print_gas_price(gas_price)
    with yaspin(text='Changing minimum delegation amount', color=SPIN_COLOR) as sp:
        new_mda_wei = to_wei(new_mda)
        tx_res = skale.validator_service.set_validator_mda(
            minimum_delegation_amount=new_mda_wei,
            wait_for=True,
            gas_price=gas_price
        )
        sp.write(f'✔ Minimum delegation amount for your validator ID changed to {new_mda}')
        print(f'Transaction hash: {tx_res.tx_hash}')


def change_address(address: str, pk_file: str, gas_price: int) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    if gas_price is None:
        gas_price = skale.gas_price
        print_gas_price(gas_price)
    with yaspin(text='Requesting new validator address', color=SPIN_COLOR) as sp:
        tx_res = skale.validator_service.request_for_new_address(
            new_validator_address=address,
            wait_for=True,
            gas_price=gas_price
        )
        sp.write(
            f'✔ Requested new address for your validator ID: {address}.\n'
            'You can finish the procedure by running < sk-val validator confirm-address > '
            'using the new key.'
        )
        print(f'Transaction hash: {tx_res.tx_hash}')


def confirm_address(validator_id: int, pk_file: str, gas_price: int) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    if gas_price is None:
        gas_price = skale.gas_price
        print_gas_price(gas_price)
    with yaspin(text='Confirming validator address change', color=SPIN_COLOR) as sp:
        tx_res = skale.validator_service.confirm_new_address(
            validator_id=validator_id,
            wait_for=True,
            gas_price=gas_price
        )
        sp.write('✔ Validator address changed')
        print(f'Transaction hash: {tx_res.tx_hash}')


def earned_fees(validator_address, wei):
    skale = init_skale_from_config()
    if not skale:
        return
    earned_fee = skale.distributor.get_earned_fee_amount(validator_address)
    earned_fee_amount = earned_fee['earned']
    earned_fee_msg = f'Earned fee for {validator_address}: '
    if not wei:
        earned_fee_amount = from_wei(earned_fee_amount)
        earned_fee_msg += f'{earned_fee_amount} SKL'
    else:
        earned_fee_msg += f'{earned_fee_amount} WEI'
    print(earned_fee_msg + f'\nEnd month: {earned_fee["end_month"]}')


def edit(name: str, description: str, pk_file: str, gas_price: int) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    if gas_price is None:
        gas_price = skale.gas_price
    print_gas_price(gas_price)

    if not name and not description:
        print('You didn\'t provide name or description, nothing will be changed')
        return

    try:
        validator_id = skale.validator_service.validator_id_by_address(skale.wallet.address)
    except ValueError:
        print(f'Validator ID is not found for your address: {skale.wallet.address}')
        sys.exit(2)

    validator = skale.validator_service.get_with_id(validator_id)

    if name:
        change_validator_name(name, skale, validator, gas_price)
    if description:
        change_validator_description(description, skale, validator, gas_price)


def change_validator_name(name, skale, validator, gas_price):
    msg = f'Changing name for validator ID {validator["id"]}: {validator["name"]} -> {name}'
    with yaspin(text=msg, color=SPIN_COLOR) as sp:
        tx_res = skale.validator_service.set_validator_name(
            new_name=name,
            wait_for=True,
            gas_price=gas_price
        )
        sp.write(f'✔ Validator name for ID {validator["id"]} changed to {name}')
        print(f'Transaction hash: {tx_res.tx_hash}')


def change_validator_description(description, skale, validator, gas_price):
    msg = f'Changing description for validator ID {validator["id"]}: \
{validator["description"]} -> {description}'
    with yaspin(text=msg, color=SPIN_COLOR) as sp:
        tx_res = skale.validator_service.set_validator_description(
            new_description=description,
            wait_for=True,
            gas_price=gas_price
        )
        sp.write(f'✔ Validator description for ID {validator["id"]} changed to {description}')
        print(f'Transaction hash: {tx_res.tx_hash}')
