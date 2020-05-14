import json
import os
import shutil

import mock
import pytest
from distutils.dir_util import copy_tree
from skale.utils.account_tools import send_ether

from cli.main import init as sk_val_init
from cli.sgx import info, init
from core.sgx import init_sgx_account
from cli.validator import _register
from utils.web3_utils import init_skale_w_wallet_from_config
from utils.helper import get_config
from utils.constants import (SGX_DATA_DIR, SKALE_VAL_CONFIG_FOLDER)
from tests.constants import (SGX_SERVER_URL, SSL_PORT,
                             D_VALIDATOR_FEE, D_VALIDATOR_DESC,
                             D_VALIDATOR_NAME,
                             D_VALIDATOR_MIN_DEL, TEST_PK_FILE)

TMP_CONFIG_FOLDER = '/tmp/.skale-val-config'


def run_sgx_init(runner, *, force=False):
    cmd = [SGX_SERVER_URL, '--ssl-port', SSL_PORT]
    if force:
        cmd.append('-f')
    return runner.invoke(init, cmd)


def sgx_inited_mock_true():
    return True


def sgx_inited_mock_false():
    return False


def sgx_init_mock(*args, **kwargs):
    return {
        'server_url': SGX_SERVER_URL,
        'ssl_port': SSL_PORT,
        'address': '0x0AAAAAAAAAAAAAAAAAAAAAAaA',
        'key': 'NEK:1232132132132321313312312321321'
    }


@mock.patch('cli.sgx.sgx_inited', sgx_inited_mock_false)
@mock.patch('cli.sgx.init_sgx_account', sgx_init_mock)
def test_init(runner):
    res = run_sgx_init(runner)
    assert res.exit_code == 0
    assert res.output == 'Sgx account created\n\x1b(0lqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqk\x1b(B\n\x1b(0x\x1b(B KEY        \x1b(0x\x1b(B VALUE                               \x1b(0x\x1b(B\n\x1b(0tqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqu\x1b(B\n\x1b(0x\x1b(B Server url \x1b(0x\x1b(B https://127.0.0.1:1026              \x1b(0x\x1b(B\n\x1b(0x\x1b(B SSL port   \x1b(0x\x1b(B 1027                                \x1b(0x\x1b(B\n\x1b(0x\x1b(B Address    \x1b(0x\x1b(B 0x0AAAAAAAAAAAAAAAAAAAAAAaA         \x1b(0x\x1b(B\n\x1b(0x\x1b(B Key        \x1b(0x\x1b(B NEK:1232132132132321313312312321321 \x1b(0x\x1b(B\n\x1b(0mqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj\x1b(B\nWARNING: If you lost the key you will be unable to access your account again\n'  # noqa


@mock.patch('cli.sgx.sgx_inited', sgx_inited_mock_true)
@mock.patch('cli.sgx.init_sgx_account', sgx_init_mock)
def test_init_already_inited(runner):
    res = run_sgx_init(runner)
    assert res.exit_code == 0
    assert res.output == 'The sgx wallet is already inited. Use --force to rewrite data\n'  # noqa

    res = run_sgx_init(runner, force=True)
    assert res.exit_code == 0
    assert res.output == 'Sgx account created\n\x1b(0lqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqk\x1b(B\n\x1b(0x\x1b(B KEY        \x1b(0x\x1b(B VALUE                               \x1b(0x\x1b(B\n\x1b(0tqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqu\x1b(B\n\x1b(0x\x1b(B Server url \x1b(0x\x1b(B https://127.0.0.1:1026              \x1b(0x\x1b(B\n\x1b(0x\x1b(B SSL port   \x1b(0x\x1b(B 1027                                \x1b(0x\x1b(B\n\x1b(0x\x1b(B Address    \x1b(0x\x1b(B 0x0AAAAAAAAAAAAAAAAAAAAAAaA         \x1b(0x\x1b(B\n\x1b(0x\x1b(B Key        \x1b(0x\x1b(B NEK:1232132132132321313312312321321 \x1b(0x\x1b(B\n\x1b(0mqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj\x1b(B\nWARNING: If you lost the key you will be unable to access your account again\n'  # noqa


def get_info_mock(*args, **kwargs):
    return {
        'server_url': SGX_SERVER_URL,
        'ssl_port': SSL_PORT,
        'address': '0x0AAAAAAAAAAAAAAAAAAAAAAaA',
        'key': 'NEK:1232132132132321313312312321321'
    }


@mock.patch('cli.sgx.get_sgx_info', get_info_mock)
@mock.patch('cli.sgx.sgx_inited', sgx_inited_mock_false)
def test_get_sgx_info_not_inited(runner):
    res = runner.invoke(info, ['--raw'])
    assert res.exit_code == 0
    assert res.output == 'SGX is not inited\n'


@mock.patch('cli.sgx.get_sgx_info', get_info_mock)
@mock.patch('cli.sgx.sgx_inited', sgx_inited_mock_true)
def test_get_sgx_info_table(runner):
    res = runner.invoke(info)
    assert res.exit_code == 0
    assert res.output == '\x1b(0lqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqk\x1b(B\n\x1b(0x\x1b(B KEY        \x1b(0x\x1b(B VALUE                               \x1b(0x\x1b(B\n\x1b(0tqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqu\x1b(B\n\x1b(0x\x1b(B Server url \x1b(0x\x1b(B https://127.0.0.1:1026              \x1b(0x\x1b(B\n\x1b(0x\x1b(B SSL port   \x1b(0x\x1b(B 1027                                \x1b(0x\x1b(B\n\x1b(0x\x1b(B Address    \x1b(0x\x1b(B 0x0AAAAAAAAAAAAAAAAAAAAAAaA         \x1b(0x\x1b(B\n\x1b(0x\x1b(B Key        \x1b(0x\x1b(B NEK:1232132132132321313312312321321 \x1b(0x\x1b(B\n\x1b(0mqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj\x1b(B\n'  # noqa


@mock.patch('cli.sgx.get_sgx_info', get_info_mock)
@mock.patch('cli.sgx.sgx_inited', sgx_inited_mock_true)
def test_get_sgx_info_raw(runner):
    res = runner.invoke(info, ['--raw'])
    assert res.exit_code == 0
    assert res.output == '{"server_url": "https://127.0.0.1:1026", "ssl_port": 1027, "address": "0x0AAAAAAAAAAAAAAAAAAAAAAaA", "key": "NEK:1232132132132321313312312321321"}\n'  # noqa


def run_val_cli_init(runner):
    if os.path.isdir(SKALE_VAL_CONFIG_FOLDER):
        copy_tree(SKALE_VAL_CONFIG_FOLDER, TMP_CONFIG_FOLDER)
        shutil.rmtree(SKALE_VAL_CONFIG_FOLDER)
    assert not os.path.isdir(SKALE_VAL_CONFIG_FOLDER)
    return runner.invoke(
        sk_val_init,
        ['-e', 'http://example.com/', '-c', 'http://example.com/',
         '-w', 'sgx']
    )


def run_validator_register(runner):
    result = runner.invoke(
        _register,
        [
            '-n', D_VALIDATOR_NAME,
            '-d', D_VALIDATOR_DESC,
            '-c', D_VALIDATOR_FEE,
            '--min-delegation', D_VALIDATOR_MIN_DEL,
            '--yes'
        ]
    )
    return result


def transfer_eth_to_sgx(skale, sgx_address):
    eth_amount = 10
    send_ether(skale.web3, skale.wallet, sgx_address, eth_amount)


@pytest.fixture
def cleanup():
    yield
    if os.path.isdir(SGX_DATA_DIR):
        shutil.rmtree(SGX_DATA_DIR)


def test_tx_with_sgx(runner, cleanup):
    config = get_config()
    get_config_mock = mock.Mock(return_value={'wallet': 'sgx',
                                              'endpoint': config['endpoint']})
    with mock.patch('utils.web3_utils.get_config', new=get_config_mock):
        res = run_validator_register(runner)
        assert res.exit_code == 0
        assert res.stdout == 'You should initialize sgx wallet first with <sk-val sgx init>\n'  # noqa

    init_sgx_account(SGX_SERVER_URL, SSL_PORT)

    # Get sgx address
    res = runner.invoke(info, ['--raw'])
    assert res.exit_code == 0
    sgx_info = json.loads(res.output.strip())

    # Using skale with Web3wallet from default config
    skale = init_skale_w_wallet_from_config(pk_file=TEST_PK_FILE)
    transfer_eth_to_sgx(skale, sgx_info['address'])

    with mock.patch('utils.web3_utils.get_config', new=get_config_mock):
        res = run_validator_register(runner)
        assert res.exit_code == 0
        assert 'New validator registered' in res.stdout
