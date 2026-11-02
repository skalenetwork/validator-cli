""" SKALE config test """

import os
import subprocess
import shutil
import time
import uuid
from subprocess import PIPE

import pytest
from click.testing import CliRunner

from skale.utils.contracts_provision.main import (
    add_test_permissions,
    add_test2_schain_type,
    setup_validator,
)
from skale.utils.contracts_provision.fake_multisig_contract import (
    deploy_fake_multisig_contract
)
from skale.utils.account_tools import send_eth
from skale.wallets.web3_wallet import generate_wallet

from tests.constants import TEST_PK_FILE, TMP_DIR
from tests.utils import get_executable_path
from utils.web3_utils import init_skale_w_wallet_from_config


@pytest.fixture(scope='session')
def tmp_dir():
    os.mkdir(TMP_DIR)
    try:
        yield TMP_DIR
    finally:
        shutil.rmtree(TMP_DIR)


def generate_filepath(parent_dir=None):
    parent_dir = parent_dir or os.path.dirname(os.path.realpath(__file__))
    return os.path.join(parent_dir, str(uuid.uuid4()))


@pytest.fixture
def tmp_filepath(tmp_dir):
    filepath = generate_filepath(parent_dir=tmp_dir)
    try:
        yield filepath
    finally:
        if os.path.isfile(filepath):
            os.remove(filepath)


@pytest.fixture
def new_wallet(skale):
    eth_amount = 0.1
    wallet = generate_wallet(skale.web3)
    send_eth(skale.web3, skale.wallet, wallet.address, eth_amount)
    return wallet


@pytest.fixture
def new_wallet_pk(new_wallet, tmp_filepath):
    with open(tmp_filepath, "w") as text_file:
        print(new_wallet._private_key, file=text_file)
    return new_wallet, tmp_filepath


@pytest.fixture(scope='session')
def skale():
    """ Returns a SKALE Manager instance with provider from config """
    skale_obj = init_skale_w_wallet_from_config(pk_file=TEST_PK_FILE)
    add_test_permissions(skale_obj)
    add_test2_schain_type(skale_obj)
    bts = skale_obj.web3.eth.get_block('latest')['timestamp']
    if bts < skale_obj.constants_holder.get_launch_timestamp():
        skale_obj.constants_holder.set_launch_timestamp(int(time.time()))
    deploy_fake_multisig_contract(skale_obj.web3, skale_obj.wallet)
    return skale_obj


@pytest.fixture(scope='session')
def validator(skale):
    vid = setup_validator(skale)
    return vid


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(scope='session')
def executable():
    cmd = ['scripts/build.sh', '0.0.0', 'test-branch']
    result = subprocess.run(cmd, shell=False, stdout=PIPE, stderr=PIPE, env={**os.environ})
    assert result.returncode == 0
    executable_path = get_executable_path()
    try:
        yield executable_path
    finally:
        os.remove(executable_path)
