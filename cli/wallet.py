import logging
import click

from core.wallet import send_eth, send_skl
from utils.helper import abort_if_false
from utils.texts import Texts

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
    send_eth(receiver_address, amount, pk_file)


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
    send_skl(receiver_address, amount, pk_file)
