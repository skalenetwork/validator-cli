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
from skale import Skale
from skale.wallets import Web3Wallet
from skale.utils.web3_utils import init_web3


def init_skale(endpoint, abi_file, private_key):
    with yaspin(text="Loading", color="yellow") as sp:
        sp.text = 'Connecting to SKALE Manager contracts'
        web3 = init_web3(endpoint)
        wallet = Web3Wallet(private_key, web3)
        skale = Skale(endpoint, abi_file, wallet)
        sp.write("✔ Connected to SKALE Manager contracts")
        return skale
