import shutil

import pytest

from core.sgx import init_sgx_account, get_sgx_info, sgx_inited
from tests.constants import SGX_SERVER_URL, SSL_PORT
from utils.constants import SGX_DATA_DIR


@pytest.fixture
def dir_cleanup():
    yield
    shutil.rmtree(SGX_DATA_DIR)


def test_generate_sgx_account(dir_cleanup):
    assert sgx_inited() is False
    info = init_sgx_account(SGX_SERVER_URL, SSL_PORT)
    keyname = info['key']
    address = info['address']
    sgx_server_url = info['server_url']
    ssl_port = info['ssl_port']
    assert len(keyname) == 68
    assert keyname.startswith('NEK:')
    assert len(address) == 42
    assert address.startswith('0x')
    assert sgx_server_url == SGX_SERVER_URL
    assert ssl_port == SSL_PORT

    info = get_sgx_info()
    expected_info = {
        'key': keyname,
        'address': address,
        'server_url': SGX_SERVER_URL,
        'ssl_port': SSL_PORT
    }
    assert info == expected_info
    assert sgx_inited() is True
