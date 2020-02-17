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

from click.testing import CliRunner
from cli.validator import _register

from skale.wallets.web3_wallet import generate_wallet
from skale.utils.account_tools import send_ether

from tests.constants import (
    D_VALIDATOR_NAME, D_VALIDATOR_DESC, D_VALIDATOR_FEE,
    D_VALIDATOR_MIN_DEL, SECOND_TEST_PK_FILE
)


def _generate_new_pk_file(skale):
    eth_amount = 0.1
    wallet = generate_wallet(skale.web3)
    send_ether(skale.web3, skale.wallet, wallet.address, eth_amount)
    with open(SECOND_TEST_PK_FILE, "w") as text_file:
        print(wallet._private_key, file=text_file)


def test_register(skale):
    _generate_new_pk_file(skale)
    n_of_validators_before = skale.validator_service.number_of_validators()

    runner = CliRunner()
    result = runner.invoke(
        _register,
        [
            '-n', D_VALIDATOR_NAME,
            '-d', D_VALIDATOR_DESC,
            '-c', D_VALIDATOR_FEE,
            '--min-delegation', D_VALIDATOR_MIN_DEL,
            '--pk-file', SECOND_TEST_PK_FILE,
            '--yes'
        ]
    )

    n_of_validators_after = skale.validator_service.number_of_validators()
    assert n_of_validators_after == n_of_validators_before + 1
    assert result.exit_code == 0
