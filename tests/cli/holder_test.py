""" Tests for cli/holder.py module """

import datetime

import pytest
from skale.utils.contracts_provision.main import _skip_evm_time
from skale.utils.contracts_provision import MONTH_IN_SECONDS

from cli.holder import (
    _delegate, _delegations, _cancel_delegation,
    _undelegate, _locked, _withdraw_bounty, _earned_bounties
)
from utils.helper import to_wei
from tests.constants import (
    TEST_PK_FILE,
    D_DELEGATION_AMOUNT,
    D_DELEGATION_PERIOD,
    D_DELEGATION_INFO
)
from tests.utils import str_contains, TEST_FEE_OPTIONS


DELEGATION_AMOUNT_SKL = 1000


def _get_number_of_delegations(skale, validator_id):
    return skale.delegation_controller._get_delegation_ids_len_by_validator(validator_id)


def test_delegate(runner, skale, validator):
    validator_id = validator
    _skip_evm_time(skale.web3, MONTH_IN_SECONDS * (D_DELEGATION_PERIOD + 1))
    num_of_delegations_before = _get_number_of_delegations(skale, validator_id)
    delegated_amount_before = skale.delegation_controller.get_delegated_amount(skale.wallet.address)
    result = runner.invoke(
        _delegate,
        [
            '--validator-id', validator_id,
            '--amount', DELEGATION_AMOUNT_SKL,
            '--delegation-period', str(D_DELEGATION_PERIOD),
            '--info', D_DELEGATION_INFO,
            '--pk-file', TEST_PK_FILE,
            '--gas-price', 1.5,
            '--yes'
        ]
    )
    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=validator_id
    )
    delegation_id = delegations[-1]['id']
    skale.delegation_controller.accept_pending_delegation(
        delegation_id,
        wait_for=True
    )
    _skip_evm_time(skale.web3, MONTH_IN_SECONDS * (D_DELEGATION_PERIOD + 1))

    delegated_amount_after = skale.delegation_controller.get_delegated_amount(skale.wallet.address)
    assert delegated_amount_after == delegated_amount_before + to_wei(DELEGATION_AMOUNT_SKL)

    num_of_delegations_after = _get_number_of_delegations(skale, validator_id)
    assert num_of_delegations_after == num_of_delegations_before + 1
    assert result.exit_code == 0


def test_delegations_skl(runner, skale):
    result = runner.invoke(
        _delegations,
        [skale.wallet.address]
    )
    output_list = result.output.splitlines()
    delegation = skale.delegation_controller.get_delegation(0)
    created_time = datetime.datetime.fromtimestamp(delegation['created'])

    assert output_list[0] == f'Delegations for address {skale.wallet.address}:'
    assert str_contains(output_list[2], [
        'Id', 'Delegator Address', 'Status', 'Validator Id', 'Amount (SKL)',
        'Delegation period (months)', 'Created At', 'Info'
    ])
    assert str_contains(output_list[4], [
        skale.wallet.address, str(created_time), delegation['info']
    ])
    assert result.exit_code == 0


def test_delegations_wei(runner, skale):
    result = runner.invoke(
        _delegations,
        [skale.wallet.address, '--wei']
    )
    output_list = result.output.splitlines()
    delegation = skale.delegation_controller.get_delegation(0)
    created_time = datetime.datetime.fromtimestamp(delegation['created'])

    assert output_list[0] == f'Delegations for address {skale.wallet.address}:'
    assert str_contains(output_list[2], [
        'Id', 'Delegator Address', 'Status', 'Validator Id', 'Amount (wei)',
        'Delegation period (months)', 'Created At', 'Info'
    ])
    assert str_contains(output_list[4], [
        skale.wallet.address, str(created_time), delegation['info'], '30000000'
    ])
    assert result.exit_code == 0


def test_cancel_delegation(runner, skale, validator):
    validator_id = validator
    skale.delegation_controller.delegate(
        validator_id=validator_id,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True
    )
    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=validator_id
    )
    delegation_id = delegations[-1]['id']
    assert delegations[-1]['status'] == 'PROPOSED'

    result = runner.invoke(
        _cancel_delegation,
        [
            str(delegation_id),
            '--yes',
            '--gas-price', 3.23,
            '--pk-file', TEST_PK_FILE,
        ]
    )

    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=validator_id
    )
    assert delegations[-1]['id'] == delegation_id
    assert delegations[-1]['status'] == 'CANCELED'
    assert result.exit_code == 0
    _skip_evm_time(skale.web3, MONTH_IN_SECONDS)


def test_undelegate(runner, skale, validator):
    validator_id = validator
    skale.delegation_controller.delegate(
        validator_id=validator_id,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True
    )
    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=validator_id
    )
    delegation_id = delegations[-1]['id']
    skale.delegation_controller.accept_pending_delegation(
        delegation_id,
        wait_for=True
    )
    _skip_evm_time(skale.web3, MONTH_IN_SECONDS * (D_DELEGATION_PERIOD + 1))

    result = runner.invoke(
        _undelegate,
        [
            str(delegation_id),
            '--yes',
            '--gas-price', 1.28,
            '--pk-file', TEST_PK_FILE
        ]
    )

    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=validator_id
    )
    assert delegations[-1]['id'] == delegation_id
    assert delegations[-1]['status'] == 'UNDELEGATION_REQUESTED'
    assert result.exit_code == 0


def test_locked(runner, skale):
    result = runner.invoke(
        _locked,
        [skale.wallet.address, '--wei']
    )
    output_list = result.output.splitlines()
    locked_amount_wei = skale.token_state.get_and_update_locked_amount(skale.wallet.address)
    expected_output = f'Locked amount for address {skale.wallet.address}:'
    assert expected_output in output_list
    assert output_list[-1] == str(locked_amount_wei)
    assert result.exit_code == 0


@pytest.mark.parametrize('fee_options', TEST_FEE_OPTIONS)
def test_withdraw_bounty(runner, skale, validator, fee_options):
    validator_id = validator
    _skip_evm_time(skale.web3, MONTH_IN_SECONDS * 3)
    recipient_address = skale.wallet.address
    result = runner.invoke(
        _withdraw_bounty,
        [
            str(validator_id),
            recipient_address,
            *fee_options,
            '--pk-file', TEST_PK_FILE,
            '--yes'
        ]
    )
    output_list = result.output.splitlines()
    expected_output = f'✔ Bounty successfully transferred to {skale.wallet.address}'
    assert expected_output in output_list
    assert result.exit_code == 0


def test_earned_bounties(runner, skale, validator):
    validator_id = validator
    earned_bounties = skale.distributor.get_earned_bounty_amount(
        validator_id,
        skale.wallet.address
    )
    result = runner.invoke(
        _earned_bounties,
        [str(validator_id), skale.wallet.address, '--wei']
    )
    output = result.output
    assert result.exit_code == 0
    assert output == f'Earned bounties for {skale.wallet.address}, validator ID - {validator_id}: {earned_bounties["earned"]} WEI\nEnd month: {earned_bounties["end_month"]}\n'  # noqa
