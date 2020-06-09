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


from yaspin import yaspin
from terminaltables import SingleTable

from utils.web3_utils import (init_skale_from_config, init_skale_w_wallet_from_config,
                              check_tx_result)
from utils.print_formatters import (print_bond_amount, print_validators,
                                    print_delegations, print_linked_addresses)
from utils.helper import to_wei, from_wei
from utils.constants import SPIN_COLOR


def register(name: str, description: str, commission_rate: int, min_delegation: int, pk_file: str):
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    with yaspin(text='Registering new validator', color=SPIN_COLOR) as sp:
        min_delegation_wei = to_wei(min_delegation)
        tx_res = skale.validator_service.register_validator(
            name=name,
            description=description,
            fee_rate=commission_rate,
            min_delegation_amount=min_delegation_wei
        )
        if not check_tx_result(tx_res.hash, skale.web3):
            sp.write(f'Transaction failed: {tx_res.hash}')
            return
        sp.write("✔ New validator registered")


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


def accept_pending_delegation(delegation_id, pk_file: str) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    with yaspin(text='Accepting delegation request', color=SPIN_COLOR) as sp:
        tx_res = skale.delegation_controller.accept_pending_delegation(
            delegation_id=delegation_id
        )
        if not check_tx_result(tx_res.hash, skale.web3):
            sp.write(f'Transaction failed: {tx_res.hash}')
            return
        sp.write(f'✔ Delegation request with ID {delegation_id} accepted')


def link_node_address(node_address: str, signature: str, pk_file: str) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    with yaspin(text='Linking node address', color=SPIN_COLOR) as sp:
        tx_res = skale.validator_service.link_node_address(
            node_address=node_address,
            signature=signature
        )
        if not check_tx_result(tx_res.hash, skale.web3):
            sp.write(f'Transaction failed: {tx_res.hash}')
            return
        sp.write(f'✔ Node address {node_address} linked to your validator address')


def unlink_node_address(node_address: str, pk_file: str) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    with yaspin(text='Unlinking node address', color=SPIN_COLOR) as sp:
        tx_res = skale.validator_service.unlink_node_address(
            node_address=node_address
        )
        if not check_tx_result(tx_res.hash, skale.web3):
            sp.write(f'Transaction failed: {tx_res.hash}')
            return
        sp.write(f'✔ Node address {node_address} unlinked from your validator address')


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
            'balance': str(skale.web3.fromWei(skale.web3.eth.getBalance(address), 'ether')),
            'nodes': len(skale.nodes_data.get_active_node_ids_by_address(address))
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
    table = SingleTable([
        ['Validator ID', validator_id],
        ['Name', validator_info['name']],
        ['Address', validator_info['validator_address']],
        ['Fee rate (%)', validator_info['fee_rate']],
        ['Minimum delegation amount (SKL)', minimum_delegation_amount],
        # ['Accepting delegation requests', accepting_delegation_requests]
    ])
    print(table.table)


def withdraw_bounty(validator_id, recipient_address, pk_file):
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    with yaspin(text='Withdrawing bounty', color=SPIN_COLOR) as sp:
        tx_res = skale.distributor.withdraw_bounty(
            validator_id=validator_id,
            to=recipient_address
        )
        if not check_tx_result(tx_res.hash, skale.web3):
            sp.write(f'Transaction failed: {tx_res.hash}')
            return
        sp.write(f'✔ Bounty successfully transferred to {recipient_address}')


def withdraw_fee(recipient_address, pk_file):
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    with yaspin(text='Withdrawing fee', color=SPIN_COLOR) as sp:
        tx_res = skale.distributor.withdraw_fee(
            to=recipient_address
        )
        if not check_tx_result(tx_res.hash, skale.web3):
            sp.write(f'Transaction failed: {tx_res.hash}')
            return
        sp.write(f'✔ Earned fees successfully transferred to {recipient_address}')


def get_bond_amount(validator_id=None):
    skale = init_skale_from_config()
    bond_amount = skale.validator_service.get_and_update_bond_amount(
        validator_id
    )
    print_bond_amount(validator_id, bond_amount)
