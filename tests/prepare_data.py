""" Preparation scripts for tests """

from skale.utils.helper import init_default_logger
from skale.utils.contracts_provision.main import setup_validator
from tests.constants import TEST_PK_FILE
from utils.web3_utils import init_skale_w_wallet_from_config


if __name__ == "__main__":
    init_default_logger()
    skale = init_skale_w_wallet_from_config(pk_file=TEST_PK_FILE)
    setup_validator(skale)
