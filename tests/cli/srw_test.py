from web3 import Web3

from cli.srw import _balance
from tests.constants import D_VALIDATOR_ID


def test_balance(runner, skale):
    amount_wei = skale.wallets.get_validator_balance(D_VALIDATOR_ID)
    amount = Web3.fromWei(amount_wei, 'ether')

    result = runner.invoke(
        _balance,
        [str(D_VALIDATOR_ID)]
    )
    output = result.output
    assert result.exit_code == 0
    assert output == f'SRW balance for validator with id {D_VALIDATOR_ID} - {amount} ETH\n'

    result = runner.invoke(
        _balance, [str(D_VALIDATOR_ID), '--wei']
    )
    output = result.output
    assert result.exit_code == 0
    assert output == f'SRW balance for validator with id {D_VALIDATOR_ID} - {amount_wei} WEI\n'
