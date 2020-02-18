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
from skale.utils.web3_utils import init_web3, wait_receipt, check_receipt

from utils.constants import SKALE_VAL_ABI_FILE, SPIN_COLOR
from utils.helper import get_config


def init_skale(endpoint, wallet=None, spin=True):
    """Init read-only instance of SKALE library"""
    if not spin:
        return Skale(endpoint, SKALE_VAL_ABI_FILE, wallet)
    with yaspin(text="Loading", color=SPIN_COLOR) as sp:
        sp.text = 'Connecting to SKALE Manager contracts'
        skale = Skale(endpoint, SKALE_VAL_ABI_FILE, wallet)
        return skale


def init_skale_w_wallet(endpoint, wallet_type, pk_file=None, spin=True):
    """Init instance of SKALE library with wallet"""
    web3 = init_web3(endpoint)
    if wallet_type == 'hardware':
        wallet = LedgerWallet(web3)
    else:
        with open(pk_file, 'r') as f:
            pk = str(f.read()).replace('\n', '')
        wallet = Web3Wallet(pk, web3)
    return init_skale(endpoint, wallet, spin)


def init_skale_from_config():
    config = get_config()
    if not config:
        print('You should run < init > first')
        return
    return init_skale(config['endpoint'])


def init_skale_w_wallet_from_config(pk_file=None):
    config = get_config()
    if not config:
        print('You should run < init > first')
        return
    if config['wallet'] == 'software' and not pk_file:
        print('Please specify path to the private key file to use software vallet with `--pk-file`\
            option')
        return
    return init_skale_w_wallet(config['endpoint'], config['wallet'], pk_file)


def get_data_from_config():
    config = get_config()
    return config['endpoint'], config['wallet']


def check_tx_result(tx_hash, web3):
    receipt = wait_receipt(web3, tx_hash)
    return check_receipt(receipt, raise_error=False)
