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

import os
import sys

from core.sgx_tools import get_sgx_info, sgx_inited
from skale import Skale
from skale.utils.exceptions import IncompatibleAbiError
from skale.utils.web3_utils import init_web3
from skale.wallets import LedgerWallet, SgxWallet, Web3Wallet
from utils.constants import SGX_SSL_CERTS_PATH, SKALE_VAL_ABI_FILE, SPIN_COLOR
from utils.helper import get_config
from yaspin import yaspin

DISABLE_SPIN = os.getenv('DISABLE_SPIN')


def init_skale(endpoint, wallet=None, disable_spin=DISABLE_SPIN):
    """Init read-only instance of SKALE library"""
    try:
        if disable_spin:
            return Skale(endpoint, SKALE_VAL_ABI_FILE, wallet)
        with yaspin(text="Loading", color=SPIN_COLOR) as sp:
            sp.text = 'Connecting to SKALE Manager contracts'
            skale = Skale(endpoint, SKALE_VAL_ABI_FILE, wallet)
            return skale
    except IncompatibleAbiError:
        print('Version of validator-cli you use is incompatible with a given ABI!')
        sys.exit(0)


def init_skale_w_wallet(endpoint, wallet_type, pk_file=None, disable_spin=DISABLE_SPIN):
    """Init instance of SKALE library with wallet"""
    web3 = init_web3(endpoint)
    if wallet_type == 'ledger':
        wallet = LedgerWallet(web3)
    elif wallet_type == 'sgx':
        info = get_sgx_info()
        wallet = SgxWallet(info['server_url'],
                           web3,
                           key_name=info['key'],
                           path_to_cert=SGX_SSL_CERTS_PATH)
    else:
        with open(pk_file, 'r') as f:
            pk = str(f.read()).strip()
        wallet = Web3Wallet(pk, web3)
    return init_skale(endpoint, wallet, disable_spin)


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
        print('Please specify path to the private key file to use software wallet with `--pk-file`\
            option')
        return
    if config['wallet'] == 'sgx' and not sgx_inited():
        print('You should initialize sgx wallet first with <sk-val sgx init>')
        return

    return init_skale_w_wallet(config['endpoint'], config['wallet'], pk_file)


def get_data_from_config():
    config = get_config()
    return config['endpoint'], config['wallet']
