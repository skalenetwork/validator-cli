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

from yaspin import yaspin
from skale import Skale
from skale.wallets import Web3Wallet, LedgerWallet
from skale.utils.web3_utils import init_web3

from cli.utils.constants import SKALE_VAL_ABI_FILE


def init_skale(endpoint, wallet=None, spin=True):
    """Init read-only instance of SKALE library"""
    if not spin:
        return Skale(endpoint, SKALE_VAL_ABI_FILE, wallet)
    with yaspin(text="Loading", color="yellow") as sp:
        sp.text = 'Connecting to SKALE Manager contracts'
        skale = Skale(endpoint, SKALE_VAL_ABI_FILE, wallet)
        return skale


def init_skale_w_wallet(endpoint, wallet_type, pk_file=None, spin=True):
    web3 = init_web3(endpoint)
    if wallet_type == 'hardware':
        wallet = LedgerWallet(web3)
    else:
        with open(pk_file, 'r') as f:
            pk = str(f.read()).replace('\n', '')
        wallet = Web3Wallet(pk, web3)
    return init_skale(endpoint, wallet, spin)
