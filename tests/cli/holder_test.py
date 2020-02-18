""" Tests for cli/holder.py module """

import datetime
from skale.dataclasses.delegation_status import DelegationStatus

from cli.holder import _delegate, _delegations, _cancel_delegation
from tests.constants import (TEST_PK_FILE, D_VALIDATOR_ID, D_DELEGATION_AMOUNT,
                             D_DELEGATION_PERIOD, D_DELEGATION_INFO)


def _get_pending_delegations(skale):
    return skale.delegation_service._get_delegation_ids_by_validator(
        skale.wallet.address,
        DelegationStatus.PROPOSED
    )


def _get_number_of_pending_delegations(skale):
    return len(_get_pending_delegations(skale))


def test_delegate(runner, skale):
    num_of_delegations_before = _get_number_of_pending_delegations(skale)
    result = runner.invoke(
        _delegate,
        [
            '--validator-id', D_VALIDATOR_ID,
            '--amount', D_DELEGATION_AMOUNT,
            '--delegation-period', str(D_DELEGATION_PERIOD),
            '--info', D_DELEGATION_INFO,
            '--pk-file', TEST_PK_FILE,
            '--yes'
        ]
    )
    num_of_delegations_after = _get_number_of_pending_delegations(skale)
    assert num_of_delegations_after == num_of_delegations_before + 1
    assert result.exit_code == 0


def test_delegations(runner, skale):
    result = runner.invoke(
        _delegations,
        [skale.wallet.address]
    )
    output_list = result.output.splitlines()
    delegation = skale.delegation_controller.get_delegation(0)
    created_time = datetime.datetime.fromtimestamp(delegation['created'])

    assert f'\x1b[KDelegations for address {skale.wallet.address}:' in output_list
    assert 'Id               Delegator Address                 Status     Validator Id   Amount (SKL)   Delegation period (months)       Created At        Info' in output_list  # noqa
    assert f'0    {skale.wallet.address}   DELEGATED   1              10000          3                            {created_time}   test' in output_list  # noqa
    assert result.exit_code == 0


def test_cancel_delegation(runner, skale):
    skale.delegation_service.delegate(
        validator_id=D_VALIDATOR_ID,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True
    )
    delegations = skale.delegation_service.get_delegations(
        skale.wallet.address,
        DelegationStatus.PROPOSED,
        'validator'
    )
    delegation_id = delegations[-1]['id']

    result = runner.invoke(
        _cancel_delegation,
        [
            str(delegation_id),
            '--pk-file', TEST_PK_FILE
        ]
    )

    delegations = skale.delegation_service.get_delegations(
        skale.wallet.address,
        DelegationStatus.COMPLETED,
        'validator'
    )
    assert delegations[-1]['id'] == delegation_id
    assert result.exit_code == 0
