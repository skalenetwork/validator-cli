""" Tests for cli/validator.py module """

import copy
import os
import random
from contextlib import contextmanager
from datetime import datetime

import mock

from web3 import Web3
from skale.wallets.web3_wallet import generate_wallet
from skale.utils.account_tools import send_ether
from skale.utils.contracts_provision.main import _skip_evm_time
from skale.utils.contracts_provision import MONTH_IN_SECONDS
from utils.helper import from_wei, permille_to_percent

from cli.validator import (_bond_amount, _register, _ls, _delegations, _accept_delegation,
                           _link_address, _unlink_address, _linked_addresses,
                           _info, _withdraw_fee, _set_mda, _change_address, _confirm_address,
                           _earned_fees, _accept_all_delegations, _edit)
from tests.conftest import str_contains
from tests.constants import (
    D_VALIDATOR_NAME, D_VALIDATOR_DESC, D_VALIDATOR_FEE, D_VALIDATOR_ID,
    D_VALIDATOR_MIN_DEL, SECOND_TEST_PK_FILE, D_DELEGATION_AMOUNT, D_DELEGATION_PERIOD,
    D_DELEGATION_INFO, TEST_PK_FILE, ADDRESS_CHANGE_PK_FILE_1, ADDRESS_CHANGE_PK_FILE_2,
    EDIT_PK_FILE_2
)
from tests.prepare_data import set_test_mda


@contextmanager
def new_wallet(skale, pk_file_path):
    eth_amount = 0.1
    wallet = generate_wallet(skale.web3)
    send_ether(skale.web3, skale.wallet, wallet.address, eth_amount)
    with open(pk_file_path, "w") as text_file:
        print(wallet._private_key, file=text_file)
    try:
        yield wallet
    finally:
        os.remove(pk_file_path)


def create_new_validator(skale, runner, pk_file_path):
    with new_wallet(skale, pk_file_path) as wallet:
        runner.invoke(
            _register,
            [
                '-n', D_VALIDATOR_NAME,
                '-d', D_VALIDATOR_DESC,
                '-c', D_VALIDATOR_FEE,
                '--min-delegation', D_VALIDATOR_MIN_DEL,
                '--pk-file', pk_file_path,
                '--gas-price', 1,
                '--yes'
            ]
        )
        return wallet


def test_register(runner, skale, validator):
    n_of_validators_before = skale.validator_service.number_of_validators()
    with new_wallet(skale, SECOND_TEST_PK_FILE) as wallet:
        result = runner.invoke(
            _register,
            [
                '-n', D_VALIDATOR_NAME,
                '-d', D_VALIDATOR_DESC,
                '-c', D_VALIDATOR_FEE,
                '--min-delegation', D_VALIDATOR_MIN_DEL,
                '--pk-file', SECOND_TEST_PK_FILE,
                '--gas-price', 1,
                '--yes'
            ]
        )
        print(result)
        validator_id = skale.validator_service.validator_id_by_address(wallet.address)
        vdata = skale.validator_service.get(validator_id)
        assert vdata['name'] == D_VALIDATOR_NAME
        assert vdata['description'] == D_VALIDATOR_DESC

        n_of_validators_after = skale.validator_service.number_of_validators()
        assert n_of_validators_after == n_of_validators_before + 1
        assert result.exit_code == 0


def check_validator_fields(expected, actual, fields):
    for i, field in enumerate(fields):
        assert str(actual[i]) == str(expected[field])


def convert_validators_info(validator_info):
    result = []
    for data in validator_info:
        info = copy.deepcopy(data)
        info['fee_rate'] = permille_to_percent(info['fee_rate'])
        info['minimum_delegation_amount'] = from_wei(
            info['minimum_delegation_amount']
        )
        info['status'] = 'Trusted' if info['trusted'] else 'Registered'
        info['registration_time'] = datetime.fromtimestamp(
            info['registration_time']
        ).strftime('%d.%m.%Y-%H:%M:%S')
        result.append(info)
    return result


def test_ls(runner, skale):
    result = runner.invoke(_ls)
    output_list = result.output.splitlines()

    validators_info = skale.validator_service.ls()
    converted_info = convert_validators_info(validators_info)
    expected_info = list(filter(lambda v: v['status'] == 'Trusted',
                                converted_info))

    header = list(filter(lambda s: s.strip().startswith('Name'), output_list))
    assert len(header) == 1
    pos = output_list.index(header[0])
    actual_info = output_list[pos + 2:]

    fields = ['name', 'id', 'validator_address', 'description', 'fee_rate',
              'registration_time', 'minimum_delegation_amount',
              'status']
    assert len(actual_info) == len(expected_info)
    for plain_actual, expected in zip(actual_info, expected_info):
        actual = plain_actual.split()
        check_validator_fields(expected, actual, fields)

    assert result.exit_code == 0


def test_ls_all(runner, skale):
    if skale.validator_service.number_of_validators() < 2:
        create_new_validator(skale, runner, SECOND_TEST_PK_FILE)

    result = runner.invoke(_ls, args="--all")
    output_list = result.output.splitlines()

    validator_info = skale.validator_service.ls()
    expected_info = convert_validators_info(validator_info)

    header = list(filter(lambda s: s.strip().startswith('Name'), output_list))
    assert len(header) == 1
    pos = output_list.index(header[0])
    actual_info = output_list[pos + 2:]

    fields = ['name', 'id', 'validator_address', 'description', 'fee_rate',
              'registration_time', 'minimum_delegation_amount',
              'status']
    assert len(actual_info) == len(expected_info)
    for plain_actual, expected in zip(actual_info, expected_info):
        actual = plain_actual.split()
        check_validator_fields(expected, actual, fields)

    assert result.exit_code == 0


def test_delegations_skl(runner, skale):
    result = runner.invoke(
        _delegations,
        [str(D_VALIDATOR_ID)]
    )
    output_list = result.output.splitlines()
    delegation = skale.delegation_controller.get_delegation(0)
    created_time = datetime.fromtimestamp(delegation['created'])
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
    created_time = datetime.fromtimestamp(delegation['created'])

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
    set_test_mda()
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
            '--gas-price', 1.7,
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


def test_accept_all_delegations(runner, skale):
    n_of_delegations = 2
    set_test_mda()
    for _ in range(n_of_delegations):
        print('Delegating...')
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

    delegation_id_1 = delegations[-1]['id']
    delegation_id_2 = delegations[-2]['id']
    assert delegations[-1]['status'] == 'PROPOSED'
    assert delegations[-2]['status'] == 'PROPOSED'

    with mock.patch('click.confirm', return_value=True):
        result = runner.invoke(
            _accept_all_delegations,
            [
                '--pk-file', TEST_PK_FILE,
                '--gas-price', 1
            ]
        )

    delegations = skale.delegation_controller.get_all_delegations_by_validator(
        validator_id=D_VALIDATOR_ID
    )
    assert delegations[-1]['id'] == delegation_id_1
    assert delegations[-1]['status'] == 'ACCEPTED'

    assert delegations[-2]['id'] == delegation_id_2
    assert delegations[-2]['status'] == 'ACCEPTED'

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
            '--gas-price', 1,
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
    assert '\x1b(0x\x1b(B Validator ID                    \x1b(0x\x1b(B 1                                          \x1b(0x\x1b(B' in output_list  # noqa
    assert '\x1b(0x\x1b(B Name                            \x1b(0x\x1b(B test                                       \x1b(0x\x1b(B' in output_list  # noqa
    assert f'\x1b(0x\x1b(B Address                         \x1b(0x\x1b(B {skale.wallet.address} \x1b(0x\x1b(B' in output_list  # noqa
    assert '\x1b(0x\x1b(B Fee rate (percent %)            \x1b(0x\x1b(B 1.0                                        \x1b(0x\x1b(B' in output_list  # noqa
    assert '\x1b(0x\x1b(B Minimum delegation amount (SKL) \x1b(0x\x1b(B 0                                          \x1b(0x\x1b(B', '\x1b(0mqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj\x1b(B'  # noqa
    # assert '\x1b(0x\x1b(B Accepting delegation requests   \x1b(0x\x1b(B Yes                                        \x1b(0x\x1b(B' in output_list  # noqa


def test_withdraw_fee(runner, skale):
    _skip_evm_time(skale.web3, MONTH_IN_SECONDS * 3)
    recipient_address = skale.wallet.address
    result = runner.invoke(
        _withdraw_fee,
        [
            recipient_address,
            '--pk-file', TEST_PK_FILE,
            '--gas-price', 1,
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
            '--gas-price', 2.9,
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
            '--gas-price', 1,
            '--yes'
        ]
    )
    output_list = result.output.splitlines()
    assert result.exit_code == 0
    assert f'\x1b[K✔ Requested new address for your validator ID: {wallet.address}.' in output_list
    assert f'You can finish the procedure by running < sk-val validator confirm-address > using the new key.' in output_list  # noqa


def test_confirm_address(runner, skale):
    wallet_1 = create_new_validator(skale, runner, ADDRESS_CHANGE_PK_FILE_1)
    with new_wallet(skale, ADDRESS_CHANGE_PK_FILE_2) as wallet_2:
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
                '--gas-price', 1,
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


def test_edit(runner, skale):
    wallet_1 = create_new_validator(skale, runner, EDIT_PK_FILE_2)
    skale.wallet = wallet_1

    new_test_name = 'test_123'
    new_test_description = 'test_description'

    latest_id = skale.validator_service.number_of_validators()
    validator = skale.validator_service.get(latest_id)

    assert validator['name'] == D_VALIDATOR_NAME
    assert validator['name'] != new_test_name
    assert validator['description'] == D_VALIDATOR_DESC
    assert validator['description'] != new_test_description

    result = runner.invoke(
        _edit,
        [
            '--name', new_test_name,
            '--description', new_test_description,
            '--pk-file', EDIT_PK_FILE_2,
            '--gas-price', 1,
            '--yes'
        ]
    )

    validator = skale.validator_service.get(latest_id)
    assert validator['name'] != D_VALIDATOR_NAME
    assert validator['name'] == new_test_name
    assert validator['description'] != D_VALIDATOR_DESC
    assert validator['description'] == new_test_description

    assert result.exit_code == 0
