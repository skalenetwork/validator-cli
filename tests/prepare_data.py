""" Preparation scripts for tests """

import random
import string
import time
from datetime import datetime

from skale.utils.contracts_provision import MONTH_IN_SECONDS
from skale.utils.contracts_provision.main import (_skip_evm_time,
                                                  cleanup_nodes_schains,
                                                  setup_validator)
from skale.utils.helper import init_default_logger

from tests.constants import (D_VALIDATOR_MIN_DEL, NODE_ID, TEST_NODE_NAME,
                             TEST_NODES_COUNT, TEST_PK_FILE)
from utils.web3_utils import init_skale_w_wallet_from_config


def generate_random_ip():
    return '.'.join('%s' % random.randint(0, 255) for i in range(4))


def generate_random_name(len=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=len))


def generate_random_port():
    return random.randint(0, 60000)


def generate_random_node_data():
    return generate_random_ip(), generate_random_ip(), generate_random_port(), \
        generate_random_name()


def create_nodes(skale, nodes_count):
    # create couple of nodes
    print(f'Creating {nodes_count} nodes')
    node_names = [TEST_NODE_NAME + str(i) for i in range(nodes_count)]
    for name in node_names:
        ip, public_ip, port, _ = generate_random_node_data()
        tx_res = skale.manager.create_node(ip, port, name, public_ip, wait_for=True)
        tx_res.raise_for_status()


def get_bounties(skale):
    go_to_next_reward_date(skale)
    tx_res = skale.manager.get_bounty(NODE_ID, wait_for=True)
    tx_res.raise_for_status()
    tx_res = skale.manager.get_bounty(NODE_ID + 1, wait_for=True)
    tx_res.raise_for_status()
    go_to_next_reward_date(skale)
    tx_res = skale.manager.get_bounty(NODE_ID, wait_for=True)
    tx_res.raise_for_status()


def go_to_next_reward_date(skale):
    reward_date = skale.nodes.contract.functions.getNodeNextRewardDate(NODE_ID).call()
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


def set_test_msr(msr=D_VALIDATOR_MIN_DEL):
    skale = init_skale_w_wallet_from_config(pk_file=TEST_PK_FILE)
    skale.constants_holder._set_msr(
        new_msr=msr,
        wait_for=True
    )
    skale.validator_service.set_validator_mda(0, wait_for=True)


def set_test_mda():
    skale = init_skale_w_wallet_from_config(pk_file=TEST_PK_FILE)
    skale.validator_service.set_validator_mda(0, wait_for=True)


def main():
    init_default_logger()
    skale = init_skale_w_wallet_from_config(pk_file=TEST_PK_FILE)
    cleanup_nodes_schains(skale)
    setup_validator(skale)
    _skip_evm_time(skale.web3, MONTH_IN_SECONDS)
    create_nodes(skale, TEST_NODES_COUNT)
    skale.constants_holder.set_launch_timestamp(int(time.time()))
    _skip_evm_time(skale.web3, MONTH_IN_SECONDS * 2)
    get_bounties(skale)


if __name__ == '__main__':
    main()
