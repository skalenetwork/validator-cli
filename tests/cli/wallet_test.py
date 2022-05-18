from skale.utils.web3_utils import to_checksum_address

from cli.wallet import _send_eth, _send_skl
from tests.constants import TEST_PK_FILE


def test_send_eth(runner, skale):
    address = skale.wallet.address
    amount = '0.01'
    amount_wei = skale.web3.toWei(amount, 'ether')

    receiver_0 = '0xf38b5dddd74b8901c9b5fb3ebd60bf5e7c1e9763'
    checksum_receiver_0 = to_checksum_address(receiver_0)
    receiver_balance_0 = skale.web3.eth.get_balance(checksum_receiver_0)
    balance_0 = skale.web3.eth.get_balance(address)
    result = runner.invoke(
        _send_eth,
        [
            receiver_0,
            amount,
            '--pk-file', TEST_PK_FILE,
            '--yes'
        ]
    )

    output_list = result.output.splitlines()
    assert result.exit_code == 0
    assert '✔ Funds were successfully transferred' in str(output_list)

    balance_1 = skale.web3.eth.get_balance(address)
    assert balance_1 < balance_0
    assert skale.web3.eth.get_balance(checksum_receiver_0) - receiver_balance_0 == amount_wei


def test_send_skl(runner):
    result = runner.invoke(
        _send_skl,
        [
            '0x01C19c5d3Ad1C3014145fC82263Fbae09e23924A',
            '0.01',
            '--pk-file', TEST_PK_FILE,
            '--yes'
        ]
    )
    output_list = result.output.splitlines()
    assert result.exit_code == 0
    assert '✔ Funds were successfully transferred' in str(output_list)
