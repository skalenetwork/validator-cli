import os

from cli.validator import _register

from tests.constants import (
    DIST_DIR,
    D_VALIDATOR_NAME,
    D_VALIDATOR_DESC,
    D_VALIDATOR_FEE,
    D_VALIDATOR_MIN_DEL,
    EXEC_PLATFORM
)

TEST_FEE_OPTIONS = [
    ('--gas-price', '1.5'),
    ('--max-fee', '1.5', '--max-priority-fee', '0.2'),
    ()
]


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


def get_executable_path(
    dist_dir=DIST_DIR,
    prefix='sk-val',
    version='0.0.0',
    platform=EXEC_PLATFORM
):
    filename = f'{prefix}-{version}-{platform}'
    return os.path.join(DIST_DIR, filename)
