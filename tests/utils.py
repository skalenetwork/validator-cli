from cli.validator import _register
from tests.constants import (
    D_VALIDATOR_NAME,
    D_VALIDATOR_DESC,
    D_VALIDATOR_FEE,
    D_VALIDATOR_MIN_DEL
)


def str_contains(string, values):
    return all(x in string for x in values)


def create_new_validator_wallet_pk(skale, runner, new_wallet_pk):
    wallet, pk = new_wallet_pk
    result = runner.invoke(
        _register,
        [
            '-n', D_VALIDATOR_NAME,
            '-d', D_VALIDATOR_DESC,
            '-c', D_VALIDATOR_FEE,
            '--min-delegation', D_VALIDATOR_MIN_DEL,
            '--pk-file', pk,
            '--yes'
        ]
    )
    assert result.exit_code == 0, result.output
    return wallet, pk
