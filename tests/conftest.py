""" SKALE config test """

import time
from datetime import datetime

import pytest
from click.testing import CliRunner

from skale import SkaleManager

from skale.utils.contracts_provision.main import (
    add_test_permissions,
    add_test2_schain_type,
    cleanup_nodes,
    cleanup_schains,
    create_nodes,
    create_schain,
    link_nodes_to_validator,
    setup_validator,
    _skip_evm_time
)
from skale.utils.account_tools import generate_account
from skale.utils.contracts_provision.fake_multisig_contract import (
    deploy_fake_multisig_contract
)
from skale.wallets import Web3Wallet

from tests.constants import TEST_PK_FILE
from utils.web3_utils import init_skale_w_wallet_from_config


NUMBER_OF_NODES = 2


@pytest.fixture(scope='session')
def skale():
    """ Returns a SKALE Manager instance with provider from config """
    skale_obj = init_skale_w_wallet_from_config(pk_file=TEST_PK_FILE)
    add_test_permissions(skale_obj)
    add_test2_schain_type(skale_obj)
    if skale_obj.constants_holder.get_launch_timestamp() == 0:
        skale_obj.constants_holder.set_launch_timestamp(int(time.time()))
    deploy_fake_multisig_contract(skale_obj.web3, skale_obj.wallet)
    return skale_obj


@pytest.fixture(scope='session')
def validator(skale):
    return setup_validator(skale)


@pytest.fixture
def node_wallets(skale):
    wallets = []
    for i in range(NUMBER_OF_NODES):
        acc = generate_account(skale.web3)
        pk = acc['private_key']
        wallet = Web3Wallet(pk, skale.web3)
        wallets.append(wallet)
    return wallets


@pytest.fixture
def node_skales(skale, node_wallets):
    return [
        SkaleManager(skale._endpoint, skale._abi_filepath, wallet)
        for wallet in node_wallets
    ]


@pytest.fixture
def nodes(skale, node_skales, validator):
    link_nodes_to_validator(skale, validator, node_skales)
    ids = create_nodes(skale)
    try:
        yield ids
    finally:
        cleanup_nodes(skale, ids)


@pytest.fixture
def schain(skale, nodes):
    try:
        yield create_schain(skale, random_name=True)
    finally:
        cleanup_schains(skale)


def get_bounties(skale, node_skales, nodes):
    go_to_next_reward_date(skale, nodes[0])
    node_skales[0].skale.manager.get_bounty(nodes[0])
    node_skales[1].skale.manager.get_bounty(nodes[1])
    go_to_next_reward_date(skale, nodes[1])
    node_skales[0].skale.manager.get_bounty(nodes[0])
    node_skales[1].skale.manager.get_bounty(nodes[1])


def go_to_next_reward_date(skale, node_id):
    reward_date = skale.nodes.contract.functions.getNodeNextRewardDate(node_id).call()
    go_to_date(skale.web3, reward_date)
    time.sleep(5)


def go_to_date(web3, date):
    block_timestamp = get_block_timestamp(web3)
    print(f'Block timestamp before: {datetime.utcfromtimestamp(block_timestamp)}')
    delta = date - block_timestamp
    _skip_evm_time(web3, delta)
    block_timestamp = get_block_timestamp(web3)
    print(f'Block timestamp after: {datetime.utcfromtimestamp(block_timestamp)}')


def get_block_timestamp(web3):
    last_block_number = web3.eth.blockNumber
    block_data = web3.eth.getBlock(last_block_number)
    return block_data['timestamp']


@pytest.fixture
def bounties(skale, node_skales, nodes):
    get_bounties(skale, node_skales, nodes)


@pytest.fixture
def runner():
    return CliRunner()


def str_contains(string, values):
    return all(x in string for x in values)
