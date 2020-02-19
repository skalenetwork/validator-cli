""" Tests for cli/validator.py module """

import datetime

from skale.dataclasses.delegation_status import DelegationStatus
from skale.wallets.web3_wallet import generate_wallet
from skale.utils.account_tools import send_ether

from cli.validator import (_register, _ls, _delegations, _accept_delegation, _link_address,
                           _unlink_address, _linked_addresses, _info)
from tests.constants import (
    D_VALIDATOR_NAME, D_VALIDATOR_DESC, D_VALIDATOR_FEE, D_VALIDATOR_ID,
    D_VALIDATOR_MIN_DEL, SECOND_TEST_PK_FILE, D_DELEGATION_AMOUNT, D_DELEGATION_PERIOD,
    D_DELEGATION_INFO, TEST_PK_FILE
)


def _generate_new_pk_file(skale):
    eth_amount = 0.1
    wallet = generate_wallet(skale.web3)
    send_ether(skale.web3, skale.wallet, wallet.address, eth_amount)
    with open(SECOND_TEST_PK_FILE, "w") as text_file:
        print(wallet._private_key, file=text_file)


def test_register(runner, skale):
    _generate_new_pk_file(skale)
    n_of_validators_before = skale.validator_service.number_of_validators()

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


def test_ls(runner, skale):
    result = runner.invoke(_ls)
    output_list = result.output.splitlines()

    validators = skale.validator_service.ls()
    registration_time = datetime.datetime.fromtimestamp(validators[0]['registration_time'])

    assert "\x1b[KName   Id                    Address                     Description   Fee rate (%)    Registration time    Minimum delegation (SKL)" in output_list  # noqa
    assert "------------------------------------------------------------------------------------------------------------------------------------" in output_list  # noqa
    assert f'test   1    {skale.wallet.address}   test          10             {registration_time}   1000                    ' in output_list  # noqa
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


def test_accept_delegation(runner, skale):
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
        _accept_delegation,
        [
            '--delegation-id', delegation_id,
            '--pk-file', TEST_PK_FILE,
            '--yes'
        ]
    )
    delegations = skale.delegation_service.get_delegations(
        skale.wallet.address,
        DelegationStatus.ACCEPTED,
        'validator'
    )
    assert delegations[-1]['id'] == delegation_id
    assert result.exit_code == 0


def test_link_address(runner, skale):
    wallet = generate_wallet(skale.web3)
    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        skale.wallet.address
    )
    assert wallet.address not in addresses

    result = runner.invoke(
        _link_address,
        [
            wallet.address,
            '--pk-file', TEST_PK_FILE,
            '--yes'
        ]
    )
    output_list = result.output.splitlines()
    expected_output = f'\x1b[K✔ Node address {wallet.address} linked to your validator address'
    assert expected_output in output_list
    assert result.exit_code == 0

    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        skale.wallet.address
    )
    assert wallet.address in addresses


def test_unlink_address(runner, skale):
    wallet = generate_wallet(skale.web3)
    skale.delegation_service.link_node_address(
        node_address=wallet.address,
        wait_for=True
    )
    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        skale.wallet.address
    )
    assert wallet.address in addresses

    result = runner.invoke(
        _unlink_address,
        [
            wallet.address,
            '--pk-file', TEST_PK_FILE,
            '--yes'
        ]
    )
    output_list = result.output.splitlines()
    expected_output = f'\x1b[K✔ Node address {wallet.address} unlinked from your validator address'
    assert expected_output in output_list
    assert result.exit_code == 0

    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        skale.wallet.address
    )
    assert wallet.address not in addresses


def test_linked_addresses(runner, skale):
    result = runner.invoke(_linked_addresses, [skale.wallet.address])
    output_list = result.output.splitlines()
    wallet_balance = str(skale.web3.fromWei(
        skale.web3.eth.getBalance(skale.wallet.address),
        'ether'
    ))

    assert f'\x1b[KLinked addresses for {skale.wallet.address}:' in output_list
    assert f'{skale.wallet.address}   Primary   {wallet_balance}   0    ' in output_list


def test_info(runner, skale):
    result = runner.invoke(_info, [str(D_VALIDATOR_ID)])
    output_list = result.output.splitlines()

    assert '\x1b(0x\x1b(B Validator ID                    \x1b(0x\x1b(B 1                                          \x1b(0x\x1b(B' in output_list  # noqa
    assert '\x1b(0x\x1b(B Name                            \x1b(0x\x1b(B test                                       \x1b(0x\x1b(B' in output_list  # noqa
    assert f'\x1b(0x\x1b(B Address                         \x1b(0x\x1b(B {skale.wallet.address} \x1b(0x\x1b(B' in output_list  # noqa
    assert '\x1b(0x\x1b(B Fee rate (%)                    \x1b(0x\x1b(B 10                                         \x1b(0x\x1b(B' in output_list  # noqa
    assert '\x1b(0x\x1b(B Minimum delegation amount (SKL) \x1b(0x\x1b(B 1000                                       \x1b(0x\x1b(B' in output_list  # noqa
    assert '\x1b(0x\x1b(B Earned bounty                   \x1b(0x\x1b(B 0                                          \x1b(0x\x1b(B' in output_list  # noqa
    assert '\x1b(0x\x1b(B MSR                             \x1b(0x\x1b(B 1000                                       \x1b(0x\x1b(B' in output_list  # noqa
