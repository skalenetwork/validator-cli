from cli.wallet import _send_eth, _send_skl
from tests.constants import TEST_PK_FILE


def test_send_eth(runner, skale):
    address = skale.wallet.address
    balance_0 = skale.web3.eth.getBalance(address)
    result = runner.invoke(
        _send_eth,
        [
            '0x01C19c5d3Ad1C3014145fC82263Fbae09e23924A',
            '0.01',
            '--pk-file', TEST_PK_FILE,
            '--yes'
        ]
    )
    balance_1 = skale.web3.eth.getBalance(address)
    assert balance_1 < balance_0

    output_list = result.output.splitlines()
    assert result.exit_code == 0
    assert output_list == ['Funds were successfully transferred']


def test_send_skl(runner, skale):
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
    assert output_list == ['Funds were successfully transferred']
