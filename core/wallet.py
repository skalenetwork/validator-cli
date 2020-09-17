import logging

from skale.utils.account_tools import send_ether, send_tokens
from skale.utils.web3_utils import to_checksum_address
from yaspin import yaspin

from utils.constants import SPIN_COLOR
from utils.web3_utils import init_skale_w_wallet_from_config
from utils.helper import print_err_with_log_path

logger = logging.getLogger(__name__)


def send_eth(receiver_address, amount, pk_file, address_index):
    _send_funds(receiver_address, amount, pk_file, 'eth', address_index)


def send_skl(receiver_address, amount, pk_file, address_index):
    _send_funds(receiver_address, amount, pk_file, 'skl', address_index)


def _send_funds(receiver_address, amount, pk_file, token_type, address_index):
    skale = init_skale_w_wallet_from_config(pk_file, address_index)
    receiver_address = to_checksum_address(receiver_address)
    with yaspin(text='Transferring funds', color=SPIN_COLOR) as sp:
        try:
            if token_type == 'eth':
                send_ether(skale.web3, skale.wallet, receiver_address, amount)
            elif token_type == 'skl':
                send_tokens(skale, skale.wallet, receiver_address, amount)
            msg = '✔ Funds were successfully transferred'
            logger.info(msg)
            sp.write(msg)
        except Exception as err:
            logger.error('Funds were not sent due to error', exc_info=err)
            sp.write('❌ Funds sending failed')
            print_err_with_log_path()
