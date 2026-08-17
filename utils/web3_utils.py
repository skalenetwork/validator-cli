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
import re
import sys
import logging

from yaspin import yaspin

from skale import SkaleManager
from skale.utils.web3_utils import init_web3
from skale_contracts.projects.skale_manager import SkaleManagerContract
from skale.wallets import LedgerWallet, SgxWallet, Web3Wallet
from skale.wallets.ledger_wallet import LedgerCommunicationError

from core.wallet_tools import get_ledger_wallet_info
from core.sgx_tools import get_sgx_info, sgx_inited
from utils.constants import SGX_SSL_CERTS_PATH, SKALE_VAL_ABI_FILE, SPIN_COLOR
from utils.helper import get_config, print_err_with_log_path, read_json

DISABLE_SPIN = os.getenv('DISABLE_SPIN')
logger = logging.getLogger(__name__)


def get_contracts_data():
    return read_json(SKALE_VAL_ABI_FILE)


def get_skale_manager_address(contracts):
    try:
        return contracts['skale_manager_address']
    except KeyError as exc:
        raise ValueError('SKALE Manager address is missing from the contracts data') from exc


def get_local_abi(contracts):
    abi = {}
    for contract_name in SkaleManagerContract:
        key = re.sub(r'(?<!^)(?=[A-Z])', '_', contract_name.value).lower() + '_abi'
        if key in contracts:
            abi[contract_name.value] = contracts[key]
    return abi


def create_skale_manager(endpoint, wallet=None):
    contracts = get_contracts_data()
    skale = SkaleManager(endpoint, get_skale_manager_address(contracts), wallet)
    local_abi = get_local_abi(contracts)
    if local_abi:
        # Prefer the deployment ABI downloaded by `sk-val init` over a remote copy.
        skale.instance._abi = local_abi
    return skale


def init_skale(endpoint, wallet=None, disable_spin=DISABLE_SPIN):
    """Init read-only instance of SKALE library"""
    if disable_spin:
        return create_skale_manager(endpoint, wallet)
    with yaspin(text="Loading", color=SPIN_COLOR) as sp:
        sp.text = 'Connecting to SKALE Manager contracts'
        return create_skale_manager(endpoint, wallet)


def init_skale_w_wallet(endpoint, wallet_type, pk_file=None, ledger_config={},
                        disable_spin=DISABLE_SPIN):
    """Init instance of SKALE library with wallet"""
    web3 = init_web3(endpoint)
    if wallet_type == 'ledger':
        try:
            legacy = ledger_config['keys_type'] == 'legacy'
            wallet = LedgerWallet(web3, ledger_config['address_index'], legacy)
        except LedgerCommunicationError as e:
            logger.exception(e)
            print_err_with_log_path(e)
            sys.exit(1)
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
    print_wallet_info(wallet)
    return init_skale(endpoint, wallet, disable_spin)


def print_wallet_info(wallet):
    print(f'Address of the account that be used for signing the transaction: {wallet.address}')
    print(f'Wallet type: {type(wallet).__name__}')


def init_skale_from_config():
    config = get_config()
    if not config:
        print('You should run < init > first')
        return
    return init_skale(config['endpoint'])


def init_skale_w_wallet_from_config(pk_file=None):
    config = get_config()
    ledger_config = get_ledger_wallet_info()
    if not config:
        print('You should run < init > first')
        return
    if config['wallet'] == 'software' and not pk_file:
        print('Please specify path to the private key file to use software wallet with `--pk-file`\
            option')
        return
    if config['wallet'] == 'ledger' and not ledger_config.get('keys_type'):
        print('Please setup Ledger wallet with < sk-val wallet setup-ledger >')
        return
    if config['wallet'] == 'sgx' and not sgx_inited():
        print('You should initialize sgx wallet first with <sk-val sgx init>')
        return

    return init_skale_w_wallet(config['endpoint'], config['wallet'], pk_file, ledger_config)


def get_data_from_config():
    config = get_config()
    return config['endpoint'], config['wallet']
