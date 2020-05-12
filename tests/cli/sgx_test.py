import mock
from cli.sgx import init

from tests.constants import SGX_SERVER_URL, SSL_PORT


def test_init(runner):
    def generate_sgx_account_mock(*args, **kwargs):
        return {
            'server_url': SGX_SERVER_URL,
            'ssl_port': SSL_PORT,
            'address': '0x0AAAAAAAAAAAAAAAAAAAAAAaA',
            'key': 'NEK:1232132132132321313312312321321'
        }

    with mock.patch('cli.sgx.init_sgx_account',
                    generate_sgx_account_mock):
        res = runner.invoke(
            init,
            [
                SGX_SERVER_URL,
                '--ssl-port', SSL_PORT
            ]
        )
        assert res.exit_code == 0
        print(repr(res.output))
        assert res.output == 'Sgx account created\n\x1b(0lqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqk\x1b(B\n\x1b(0x\x1b(B KEY        \x1b(0x\x1b(B VALUE                               \x1b(0x\x1b(B\n\x1b(0tqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqu\x1b(B\n\x1b(0x\x1b(B Server url \x1b(0x\x1b(B https://127.0.0.1:1026              \x1b(0x\x1b(B\n\x1b(0x\x1b(B SSL port   \x1b(0x\x1b(B 1027                                \x1b(0x\x1b(B\n\x1b(0x\x1b(B Address    \x1b(0x\x1b(B 0x0AAAAAAAAAAAAAAAAAAAAAAaA         \x1b(0x\x1b(B\n\x1b(0x\x1b(B Key        \x1b(0x\x1b(B NEK:1232132132132321313312312321321 \x1b(0x\x1b(B\n\x1b(0mqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj\x1b(B\nWARNING: If you lost the key you will be unable to access your account again\n'  # noqa
