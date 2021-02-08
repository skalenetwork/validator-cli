#   -*- coding: utf-8 -*-
#
#   This file is part of validator-cli
#
#   Copyright (C) 2021 SKALE Labs
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
from skale.transactions.result import TransactionError

from utils.web3_utils import init_skale_from_config, init_skale_w_wallet_from_config
from utils.helper import to_wei, print_gas_price
from utils.print_formatters import print_srw_balance
from utils.constants import SPIN_COLOR


def recharge(amount: str, pk_file: str, gas_price: int) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    if gas_price is None:
        gas_price = skale.gas_price
        print_gas_price(gas_price)
    with yaspin(text='Recharging ETH from validator SRW wallet', color=SPIN_COLOR) as sp:
        # amount_wei = to_wei(amount)
        _ = to_wei(amount)
        # todo!
        tx_res = skale.wallets.recharge(
            gas_price=gas_price,
            raise_for_status=False
        )
        try:
            tx_res.raise_for_status()
        except TransactionError as err:
            sp.write(str(err))
            return
        sp.write("✔ Wallet recharged")
        print(f'Transaction hash: {tx_res.tx_hash}')


def withdraw(amount: str, pk_file: str, gas_price: int) -> None:
    skale = init_skale_w_wallet_from_config(pk_file)
    if not skale:
        return
    if gas_price is None:
        gas_price = skale.gas_price
        print_gas_price(gas_price)
    with yaspin(text='Withdrawing ETH from validator SRW wallet', color=SPIN_COLOR) as sp:
        # amount_wei = to_wei(amount)
        _ = to_wei(amount)
        # todo
        tx_res = skale.wallets.recharge(
            gas_price=gas_price,
            raise_for_status=False
        )
        try:
            tx_res.raise_for_status()
        except TransactionError as err:
            sp.write(str(err))
            return
        sp.write("✔ ETH withdrawn")
        print(f'Transaction hash: {tx_res.tx_hash}')


def balance(validator_id, wei=False):
    skale = init_skale_from_config()
    srw_balance = skale.wallets.get_validator_balance(validator_id)
    print_srw_balance(validator_id, srw_balance, wei)
