import json
import logging
import os

from sgx import SgxClient

from utils.constants import SGX_SSL_CERTS_PATH, SGX_INFO_PATH

logger = logging.getLogger(__name__)


class SGXError(Exception):
    pass


def sgx_inited() -> bool:
    return os.path.isdir(SGX_SSL_CERTS_PATH)


def get_sgx_info() -> dict:
    if not os.path.isfile(SGX_INFO_PATH):
        return {}
    with open(SGX_INFO_PATH) as info_file:
        return json.load(info_file)


def save_sgx_info(key_info, sgx_server_url, ssl_port):
    with open(SGX_INFO_PATH, 'w') as info_file:
        data_to_dump = {'key': key_info.name, 'address': key_info.address}
        data_to_dump['server_url'] = sgx_server_url
        data_to_dump['ssl_port'] = ssl_port
        json.dump(data_to_dump, info_file)


def generate_sgx_key(sgx_server_url, ssl_port) -> tuple:
    if not os.path.isdir(SGX_SSL_CERTS_PATH):
        os.makedirs(SGX_SSL_CERTS_PATH)

    if ssl_port is not None:
        client = SgxClient(sgx_server_url, SGX_SSL_CERTS_PATH)
    else:
        client = SgxClient(sgx_server_url)
    return client.generate_key()


def init_sgx_account(sgx_server_url, ssl_port):
    key_info = generate_sgx_key(sgx_server_url, ssl_port)
    save_sgx_info(key_info, sgx_server_url, ssl_port)
    return get_sgx_info()
