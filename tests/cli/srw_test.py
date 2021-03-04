import mock
from web3 import Web3

from cli.srw import _balance, _recharge, _withdraw
from utils.helper import to_wei
from tests.constants import D_VALIDATOR_ID, TEST_PK_FILE
from tests.cli.validator_test import create_new_validator
from tests.constants import RECHARGE_PK_FILE

TEST_RECHARGE_VALUE_ETH = '0.1'


def test_balance(runner, skale):
    amount_wei = skale.wallets.get_validator_balance(D_VALIDATOR_ID)
    amount = Web3.fromWei(amount_wei, 'ether')

    result = runner.invoke(
        _balance,
        [str(D_VALIDATOR_ID)]
    )
    output = result.output
    assert result.exit_code == 0
    assert output == f'SRW balance for validator with id {D_VALIDATOR_ID} - {amount} ETH\n'

    result = runner.invoke(
        _balance, [str(D_VALIDATOR_ID), '--wei']
    )
    output = result.output
    assert result.exit_code == 0
    assert output == f'SRW balance for validator with id {D_VALIDATOR_ID} - {amount_wei} WEI\n'


def test_recharge(runner, skale):
    amount_before = skale.wallets.get_validator_balance(D_VALIDATOR_ID)
    with mock.patch('click.confirm', return_value=True):
        result = runner.invoke(
            _recharge,
            [
                str(TEST_RECHARGE_VALUE_ETH),
                '--pk-file', TEST_PK_FILE
            ]
        )

    amount_after = skale.wallets.get_validator_balance(D_VALIDATOR_ID)
    assert amount_after == amount_before + to_wei(TEST_RECHARGE_VALUE_ETH)
    assert '✔ Wallet recharged' in result.output
    assert result.exit_code == 0

    with mock.patch('click.confirm', return_value=True):
        result = runner.invoke(
            _recharge,
            [
                str(TEST_RECHARGE_VALUE_ETH),
                '--pk-file', TEST_PK_FILE,
                '--gas-price', 1.67
            ]
        )
    assert '✔ Wallet recharged' in result.output
    assert result.exit_code == 0


def test_recharge_custom_validator(runner, skale):
    create_new_validator(skale, runner, RECHARGE_PK_FILE)
    latest_validator_id = skale.validator_service.number_of_validators()

    amount_before = skale.wallets.get_validator_balance(latest_validator_id)
    assert amount_before == 0
    with mock.patch('click.confirm', return_value=True):
        result = runner.invoke(
            _recharge,
            [
                str(TEST_RECHARGE_VALUE_ETH),
                '--validator-id', latest_validator_id,
                '--pk-file', TEST_PK_FILE
            ]
        )
    amount_after = skale.wallets.get_validator_balance(latest_validator_id)
    assert amount_after == amount_before + to_wei(TEST_RECHARGE_VALUE_ETH)
    assert '✔ Wallet recharged' in result.output
    assert result.exit_code == 0


def test_withdraw(runner, skale):
    test_recharge_value_wei = to_wei(TEST_RECHARGE_VALUE_ETH)
    skale.wallets.recharge_validator_wallet(D_VALIDATOR_ID, value=test_recharge_value_wei)
    amount_before = skale.wallets.get_validator_balance(D_VALIDATOR_ID)

    with mock.patch('click.confirm', return_value=True):
        result = runner.invoke(
            _withdraw,
            [
                str(TEST_RECHARGE_VALUE_ETH),
                '--pk-file', TEST_PK_FILE
            ]
        )

    amount_after = skale.wallets.get_validator_balance(D_VALIDATOR_ID)
    assert amount_after == amount_before - to_wei(TEST_RECHARGE_VALUE_ETH)
    assert '✔ ETH withdrawn' in result.output
    assert result.exit_code == 0
