""" SKALE config test """

import pytest
from click.testing import CliRunner

from utils.web3_utils import init_skale_w_wallet_from_config
from tests.constants import TEST_PK_FILE


@pytest.fixture
def skale():
    '''Returns a SKALE instance with provider from config'''
    return init_skale_w_wallet_from_config(pk_file=TEST_PK_FILE)


@pytest.fixture
def runner():
    return CliRunner()
