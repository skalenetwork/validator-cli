import subprocess
import sys

from click.testing import CliRunner

from cli.validator import _ls, _register


def test_legacy_abi_parser_runs_on_python_314():
    result = subprocess.run(
        [
            sys.executable,
            '-c',
            'import cli; from eth_abi import decode_abi; '
            'assert decode_abi(["uint256"], bytes(32)) == (0,)',
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert 'pkg_resources is deprecated' not in result.stderr


def test_validator_ls_invokes_service(monkeypatch):
    calls = []
    monkeypatch.setattr('cli.validator.validators_list', lambda wei, all: calls.append((wei, all)))

    result = CliRunner().invoke(_ls, ['--wei', '--all'])

    assert result.exit_code == 0
    assert calls == [(True, True)]


def test_validator_register_invokes_service(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr('cli.validator.register', lambda **kwargs: calls.append(kwargs))
    key_file = tmp_path / 'validator.key'
    key_file.write_text('private-key')

    result = CliRunner().invoke(
        _register,
        [
            '--name', 'validator',
            '--description', 'description',
            '--commission-rate', '1.5',
            '--min-delegation', '1000',
            '--pk-file', str(key_file),
            '--yes',
        ],
    )

    assert result.exit_code == 0
    assert len(calls) == 1
    assert calls[0]['name'] == 'validator'
    assert calls[0]['description'] == 'description'
    assert calls[0]['commission_rate'] == 1.5
    assert calls[0]['min_delegation'] == 1000
    assert calls[0]['pk_file'] == str(key_file)
    assert calls[0]['fee'].gas_price is None
