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

import dataclasses
from typing import Optional

from yaspin import yaspin
from skale.utils.web3_utils import to_checksum_address

from core.transaction import TxFee
from utils.helper import to_skl
from utils.web3_utils import (init_skale_from_config,
                              init_skale_w_wallet_from_config)
from utils.print_formatters import print_delegations
from utils.helper import to_wei, from_wei
from utils.constants import SPIN_COLOR


def delegations(address, wei):
    checksum_address = to_checksum_address(address)
    skale = init_skale_from_config()
    if not skale:
        return
    delegations_list = skale.delegation_controller.get_all_delegations_by_holder(
        checksum_address
    )
    print(f'Delegations for address {address}:\n')
    print_delegations(delegations_list, wei)


def delegate(validator_id: int, amount: int, delegation_period: int, info: str,
             pk_file: str, fee: Optional[TxFee]) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    fee = fee or TxFee(gas_price=skale.gas_price)
    with yaspin(text='Sending delegation request', color=SPIN_COLOR) as sp:
        amount_wei = to_wei(amount)
        tx_res = skale.delegation_controller.delegate(
            validator_id=validator_id,
            amount=amount_wei,
            delegation_period=delegation_period,
            info=info,
            **dataclasses.asdict(fee)
        )
        sp.write("✔ Delegation request sent")
        print(f'Transaction hash: {tx_res.tx_hash}')


def cancel_pending_delegation(delegation_id: int, pk_file: str,
                              fee: Optional[TxFee]) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    fee = fee or TxFee(gas_price=skale.gas_price)
    with yaspin(text='Canceling delegation request', color=SPIN_COLOR) as sp:
        tx_res = skale.delegation_controller.cancel_pending_delegation(
            delegation_id=delegation_id,
            **dataclasses.asdict(fee)
        )
        sp.write("✔ Delegation request canceled")
        print(f'Transaction hash: {tx_res.tx_hash}')


def undelegate(delegation_id: int, pk_file: str, fee: Optional[TxFee]) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    fee = fee or TxFee(gas_price=skale.gas_price)
    with yaspin(text='Requesting undelegation', color=SPIN_COLOR) as sp:
        tx_res = skale.delegation_controller.request_undelegation(
            delegation_id=delegation_id,
            **dataclasses.asdict(fee)
        )
        sp.write("✔ Successfully undelegated")
        print(f'Transaction hash: {tx_res.tx_hash}')


def withdraw_bounty(validator_id: int, recipient_address: str,
                    pk_file: str, fee: Optional[TxFee]) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    fee = fee or TxFee(gas_price=skale.gas_price)
    with yaspin(text='Withdrawing bounty', color=SPIN_COLOR) as sp:
        tx_res = skale.distributor.withdraw_bounty(
            validator_id=validator_id,
            to=recipient_address,
            **dataclasses.asdict(fee)
        )
        sp.write(f'✔ Bounty successfully transferred to {recipient_address}')
        print(f'Transaction hash: {tx_res.tx_hash}')


def locked(address, wei):
    skale = init_skale_from_config()
    if not skale:
        return
    locked_amount_wei = skale.token_state.get_and_update_locked_amount(address)
    amount = locked_amount_wei if wei else to_skl(locked_amount_wei)
    print(f'Locked amount for address {address}:\n{amount}')


def earned_bounties(validator_id, address, wei):
    skale = init_skale_from_config()
    if not skale:
        return
    earned_bounties_data = skale.distributor.get_earned_bounty_amount(validator_id, address)
    earned_bounties_amount = earned_bounties_data['earned']
    earned_bounties_msg = f'Earned bounties for {address}, validator ID - {validator_id}: '
    if not wei:
        earned_bounties_amount = from_wei(earned_bounties_amount)
        earned_bounties_msg += f'{earned_bounties_amount} SKL'
    else:
        earned_bounties_msg += f'{earned_bounties_amount} WEI'
    print(earned_bounties_msg + f'\nEnd month: {earned_bounties_data["end_month"]}')
