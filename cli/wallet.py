import click
from utils.texts import Texts

G_TEXTS = Texts()
TEXTS = G_TEXTS['wallet']
MSGS = G_TEXTS['msg']


@click.group()
def wallet_cli():
    pass


@wallet_cli.group('wallet', help=TEXTS['help'])
def wallet():
    pass


@wallet.command('send-eth', help=TEXTS['send_eth']['help'])
@click.argument('receiver_address')
@click.argument('amount')
def _send_eth(receiver_address, amount):
    pass


@wallet.command('send-skl', help=TEXTS['send_skl']['help'])
@click.argument('receiver_address')
@click.argument('amount')
def _send_eth(receiver_address, amount):
    pass
