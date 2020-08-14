import logging
import click
from skale.utils.web3_utils import to_checksum_address

from utils.helper import abort_if_false
from utils.texts import Texts
from utils.web3_utils import init_skale_w_wallet_from_config
from skale.utils.account_tools import send_ether, send_tokens

G_TEXTS = Texts()
TEXTS = G_TEXTS['wallet']

logger = logging.getLogger(__name__)


@click.group()
def wallet_cli():
    pass


@wallet_cli.group('wallet', help=TEXTS['help'])
def wallet():
    pass


@wallet.command('send-eth', help=TEXTS['send_eth']['help'])
@click.argument('receiver_address')
@click.argument('amount')
@click.option(
    '--pk-file',
    help=G_TEXTS['pk_file']['help']
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False, prompt=TEXTS['send_eth']['confirm'])
def _send_eth(receiver_address, amount, pk_file):
    skale = init_skale_w_wallet_from_config(pk_file)
    try:
        receiver_address = to_checksum_address(receiver_address)
        send_ether(skale.web3, skale.wallet, receiver_address, amount)
        msg = TEXTS['send_eth']['success']
        logger.info(msg)
        print(msg)
    except Exception as err:
        logger.error('Funds were not sent due to error', exc_info=err)
        print(TEXTS['send_eth']['error'])


@wallet.command('send-skl', help=TEXTS['send_skl']['help'])
@click.argument('receiver_address')
@click.argument('amount')
@click.option(
    '--pk-file',
    help=G_TEXTS['pk_file']['help']
)
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False, prompt=TEXTS['send_skl']['confirm'])
def _send_skl(receiver_address, amount, pk_file):
    skale = init_skale_w_wallet_from_config(pk_file)
    try:
        receiver_address = to_checksum_address(receiver_address)
        send_tokens(skale, skale.wallet, receiver_address, amount)
        msg = TEXTS['send_skl']['success']
        logger.info(msg)
        print(msg)
    except Exception as err:
        logger.error('Funds were not sent due to error', exc_info=err)
        print(TEXTS['send_skl']['error'])
