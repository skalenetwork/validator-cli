""" Tests for cli/validator.py module """

import random
import datetime

from skale.wallets.web3_wallet import generate_wallet
from skale.utils.account_tools import send_ether
from skale.utils.contracts_provision.main import _skip_evm_time
from skale.utils.contracts_provision import MONTH_IN_SECONDS
from web3 import Web3

from cli.validator import (_bond_amount, _register, _ls, _delegations, _accept_delegation,
                           _link_address, _unlink_address, _linked_addresses,
                           _info, _withdraw_fee, _set_mda, _change_address, _confirm_address,
                           _earned_fees)
from tests.conftest import str_contains
from tests.constants import (
    D_VALIDATOR_NAME, D_VALIDATOR_DESC, D_VALIDATOR_FEE, D_VALIDATOR_ID,
    D_VALIDATOR_MIN_DEL, SECOND_TEST_PK_FILE, D_DELEGATION_AMOUNT, D_DELEGATION_PERIOD,
    D_DELEGATION_INFO, TEST_PK_FILE, ADDRESS_CHANGE_PK_FILE_1, ADDRESS_CHANGE_PK_FILE_2
)


def create_new_validator(skale, runner, pk_file_path):
    wallet = _generate_new_pk_file(skale, pk_file_path)
    runner.invoke(
        _register,
        [
            '-n', D_VALIDATOR_NAME,
            '-d', D_VALIDATOR_DESC,
            '-c', D_VALIDATOR_FEE,
            '--min-delegation', D_VALIDATOR_MIN_DEL,
            '--pk-file', pk_file_path,
            '--yes'
        ]
    )
    return wallet


def _generate_new_pk_file(skale, pk_file_path):
    eth_amount = 0.1
    wallet = generate_wallet(skale.web3)
    send_ether(skale.web3, skale.wallet, wallet.address, eth_amount)
    with open(pk_file_path, "w") as text_file:
        print(wallet._private_key, file=text_file)
    return wallet


def test_register(runner, skale):
    n_of_validators_before = skale.validator_service.number_of_validators()
    _generate_new_pk_file(skale, SECOND_TEST_PK_FILE)
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
    registration_time = datetime.datetime.fromtimestamp(
        validators[0]['registration_time'])
    assert "Name   Id                    Address                     Description   Fee rate (permille)    Registration time    Minimum delegation (SKL)   Validator status" in output_list  # noqa
    assert "--------------------------------------------------------------------------------------------------------------------------------------------------------------" in output_list  # noqa
    assert f'test   1    {skale.wallet.address}   test          10                    {registration_time}   1E-12                      Trusted         ' in output_list  # noqa
    #assert f'test   1    {skale.wallet.address}   test          10             {registration_time}   1E-12                      Trusted         ' in output_list  # noqa
    assert result.exit_code == 0


def test_ls_all(runner, skale):
    if skale.validator_service.number_of_validators() < 2:
        create_new_validator(skale, runner, SECOND_TEST_PK_FILE)

    result = runner.invoke(_ls, args="--all")
    output_list = result.output.splitlines()

    validators = skale.validator_service.ls()
    registration_time = list(map(lambda x: datetime.datetime.fromtimestamp(x['registration_time']),
                                 validators))
    assert "Name   Id                    Address                     Description   Fee rate (permille)    Registration time    Minimum delegation (SKL)   Validator status" in output_list  # noqa
    assert "--------------------------------------------------------------------------------------------------------------------------------------------------------------" in output_list  # noqa
    assert f'test   1    {validators[0]["validator_address"]}   test          10                    {registration_time[0]}   1E-12                      Trusted         ' in output_list  # noqa
    assert f'test   2    {validators[1]["validator_address"]}   test          10                    {registration_time[1]}   1000                       Registered      ' in output_list  # noqa
    assert result.exit_code == 0


def test_delegations_skl(runner, skale):
    result = runner.invoke(
        _delegations,
        [str(D_VALIDATOR_ID)]
    )
    output_list = result.output.splitlines()
    delegation = skale.delegation_controller.get_delegation(0)
    created_time = datetime.datetime.fromtimestamp(delegation['created'])
    assert output_list[0] == f'Delegations for validator ID {D_VALIDATOR_ID}:'
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
        [str(D_VALIDATOR_ID), '--wei']
    )
    output_list = result.output.splitlines()
    delegation = skale.delegation_controller.get_delegation(0)
    created_time = datetime.datetime.fromtimestamp(delegation['created'])

    assert output_list[0] == f'Delegations for validator ID {D_VALIDATOR_ID}:'
    assert str_contains(output_list[2], [
        'Id', 'Delegator Address', 'Status', 'Validator Id', 'Amount (wei)',
        'Delegation period (months)', 'Created At', 'Info'
    ])
    assert str_contains(output_list[4], [
        skale.wallet.address, str(created_time), delegation['info'], '30000000'
    ])
    assert result.exit_code == 0


def test_accept_delegation(runner, skale):
    skale.delegation_controller.delegate(
        validator_id=D_VALIDATOR_ID,
        amount=D_DELEGATION_AMOUNT,
        delegation_period=D_DELEGATION_PERIOD,
        info=D_DELEGATION_INFO,
        wait_for=True
    )
    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=D_VALIDATOR_ID
    )
    delegation_id = delegations[-1]['id']
    assert delegations[-1]['status'] == 'PROPOSED'

    result = runner.invoke(
        _accept_delegation,
        [
            '--delegation-id', delegation_id,
            '--pk-file', TEST_PK_FILE,
            '--yes'
        ]
    )

    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=D_VALIDATOR_ID
    )
    assert delegations[-1]['id'] == delegation_id
    assert delegations[-1]['status'] == 'ACCEPTED'
    assert result.exit_code == 0
    _skip_evm_time(skale.web3, MONTH_IN_SECONDS)


def test_link_address(runner, skale):
    wallet = generate_wallet(skale.web3)
    addresses = skale.validator_service.get_linked_addresses_by_validator_address(
        skale.wallet.address
    )
    assert wallet.address not in addresses

    main_wallet = skale.wallet
    skale.wallet = wallet
    signature = skale.validator_service.get_link_node_signature(
        validator_id=D_VALIDATOR_ID
    )
    skale.wallet = main_wallet

    result = runner.invoke(
        _link_address,
        [
            wallet.address,
            signature,
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

    main_wallet = skale.wallet
    skale.wallet = wallet
    signature = skale.validator_service.get_link_node_signature(
        validator_id=D_VALIDATOR_ID
    )
    skale.wallet = main_wallet

    skale.validator_service.link_node_address(
        node_address=wallet.address,
        signature=signature,
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
    # wallet_balance = str(skale.web3.fromWei(
    #     skale.web3.eth.getBalance(skale.wallet.address),
    #     'ether'
    # ))

    assert f'Linked addresses for {skale.wallet.address}:' in output_list
    # todo: impove test


def test_info(runner, skale):
    result = runner.invoke(_info, [str(D_VALIDATOR_ID)])
    output_list = result.output.splitlines()

    print(output_list)
    assert result.exit_code == 0
    assert '\x1b(0x\x1b(B Validator ID                     \x1b(0x\x1b(B 1                                          \x1b(0x\x1b(B' in output_list  # noqa
    assert '\x1b(0x\x1b(B Name                             \x1b(0x\x1b(B test                                       \x1b(0x\x1b(B' in output_list  # noqa
    assert f'\x1b(0x\x1b(B Address                          \x1b(0x\x1b(B {skale.wallet.address} \x1b(0x\x1b(B' in output_list  # noqa
    assert '\x1b(0x\x1b(B Fee rate (permille - permille ‰) \x1b(0x\x1b(B 10                                         \x1b(0x\x1b(B' in output_list  # noqa
    assert '\x1b(0x\x1b(B Minimum delegation amount (SKL)  \x1b(0x\x1b(B 1E-12                                      \x1b(0x\x1b(B' in output_list  # noqa
    # assert '\x1b(0x\x1b(B Accepting delegation requests   \x1b(0x\x1b(B Yes                                        \x1b(0x\x1b(B' in output_list  # noqa


def test_withdraw_fee(runner, skale):
    _skip_evm_time(skale.web3, MONTH_IN_SECONDS * 3)
    recipient_address = skale.wallet.address
    result = runner.invoke(
        _withdraw_fee,
        [
            recipient_address,
            '--pk-file', TEST_PK_FILE,
            '--yes'
        ]
    )
    output_list = result.output.splitlines()
    expected_output = f'\x1b[K✔ Earned fees successfully transferred to {skale.wallet.address}'
    assert expected_output in output_list
    assert result.exit_code == 0


def test_bond_amount(runner, skale):
    bond_wei = skale.validator_service.get_and_update_bond_amount(D_VALIDATOR_ID)
    bond = Web3.fromWei(bond_wei, 'ether')

    result = runner.invoke(
        _bond_amount,
        [str(D_VALIDATOR_ID)]
    )
    output = result.output
    assert result.exit_code == 0
    assert output == f'Bond amount for validator with id {D_VALIDATOR_ID} - {bond} SKL\n'

    result = runner.invoke(
        _bond_amount, [str(D_VALIDATOR_ID), '--wei']
    )
    output = result.output
    assert result.exit_code == 0
    assert output == f'Bond amount for validator with id {D_VALIDATOR_ID} - {bond_wei} WEI\n'


def test_set_mda(runner):
    minimum_delegation_amount = str(random.randint(1000, 10000))
    result = runner.invoke(
        _set_mda,
        [
            minimum_delegation_amount,
            '--pk-file', TEST_PK_FILE,
            '--yes'
        ]
    )
    output_list = result.output.splitlines()
    assert result.exit_code == 0
    assert f'\x1b[K✔ Minimum delegation amount for your validator ID changed to {minimum_delegation_amount}.0' in output_list  # noqa


def test_change_address(runner, skale):
    wallet = generate_wallet(skale.web3)
    result = runner.invoke(
        _change_address,
        [
            wallet.address,
            '--pk-file', TEST_PK_FILE,
            '--yes'
        ]
    )
    output_list = result.output.splitlines()
    assert result.exit_code == 0
    assert f'\x1b[K✔ Requested new address for your validator ID: {wallet.address}.' in output_list
    assert f'You can finish the procedure by running < sk-val validator confirm-address > using the new key.' in output_list  # noqa


def test_confirm_address(runner, skale):
    wallet_1 = create_new_validator(skale, runner, ADDRESS_CHANGE_PK_FILE_1)
    wallet_2 = _generate_new_pk_file(skale, ADDRESS_CHANGE_PK_FILE_2)

    main_wallet = skale.wallet
    skale.wallet = wallet_1
    skale.validator_service.request_for_new_address(
        new_validator_address=wallet_2.address,
        wait_for=True
    )
    skale.wallet = main_wallet
    latest_validator_id = skale.validator_service.number_of_validators()

    result = runner.invoke(
        _confirm_address,
        [
            str(latest_validator_id),
            '--pk-file', ADDRESS_CHANGE_PK_FILE_2,
            '--yes'
        ]
    )
    output_list = result.output.splitlines()
    assert result.exit_code == 0
    assert '\x1b[K✔ Validator address changed' in output_list


def test_earned_fees(runner, skale):
    earned_fee = skale.distributor.get_earned_fee_amount(skale.wallet.address)
    result = runner.invoke(
        _earned_fees,
        [skale.wallet.address, '--wei']
    )
    output = result.output
    assert result.exit_code == 0
    assert output == f'Earned fee for {skale.wallet.address}: {earned_fee["earned"]} WEI\nEnd month: {earned_fee["end_month"]}\n'  # noqa
