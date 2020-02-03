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
from skale.utils.web3_utils import wait_receipt, check_receipt

from utils.web3_utils import init_skale_from_config, init_skale_w_wallet_from_config
from utils.print_formatters import print_delegations
from utils.constants import SPIN_COLOR


def delegations(address):
    skale = init_skale_from_config()
    if not skale:
        return
    delegations_list = skale.delegation_service.get_all_delegations_by_holder(address)
    print(f'Delegations for address {address}:\n')
    print_delegations(delegations_list)


def delegate(validator_id, amount, delegation_period, info, pk_file):
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    with yaspin(text='Sending delegation request', color=SPIN_COLOR) as sp:
        tx_res = skale.delegation_service.delegate(
            validator_id=validator_id,
            amount=amount,
            delegation_period=delegation_period,
            info=info
        )
        receipt = wait_receipt(skale.web3, tx_res.hash)
        if not check_receipt(receipt, raise_error=False):
            sp.write(f'Transaction failed, check receipt: {tx_res.hash}')
            return
        sp.write("✔ Delegation request sent")


def cancel_pending_delegation(delegation_id: int, pk_file: str) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    with yaspin(text='Canceling delegation request', color=SPIN_COLOR) as sp:
        tx_res = skale.delegation_service.cancel_pending_delegation(
            delegation_id=delegation_id
        )
        receipt = wait_receipt(skale.web3, tx_res.hash)
        if not check_receipt(receipt, raise_error=False):
            sp.write(f'Transaction failed, check receipt: {tx_res.hash}')
            return
        sp.write("✔ Delegation request canceled")
