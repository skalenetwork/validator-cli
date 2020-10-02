""" Constants for tests """

import os


HERE = os.path.dirname(os.path.realpath(__file__))
TEST_PK_FILE = os.path.join(HERE, 'test-pk.txt')
SECOND_TEST_PK_FILE = os.path.join(HERE, 'second-test-pk.txt')

ADDRESS_CHANGE_PK_FILE_1 = os.path.join(HERE, 'ch-test-pk-1.txt')
ADDRESS_CHANGE_PK_FILE_2 = os.path.join(HERE, 'ch-test-pk-2.txt')
EDIT_PK_FILE_2 = os.path.join(HERE, 'edit-test-pk-2.txt')

PROJECT_DIR = os.path.join(HERE, os.pardir)
DIST_DIR = os.path.join(PROJECT_DIR, 'dist')

# validator

D_VALIDATOR_ID = 1
D_VALIDATOR_NAME = 'test'
D_VALIDATOR_DESC = 'test'
D_VALIDATOR_FEE = 10.5
D_VALIDATOR_MIN_DEL = 1000

D_DELEGATION_ID = 0
D_DELEGATION_AMOUNT = 55000000
D_DELEGATION_PERIOD = 2
D_DELEGATION_INFO = 'test'

TEST_CHECKTIME = 30
TEST_EPOCH = 40
TEST_DELTA = 10
TEST_NODE_NAME = 'test_node'
NODE_ID = 0
TEST_NODES_COUNT = 2
SERVICE_ROW_COUNT = 4

SGX_SERVER_URL = os.getenv('SGX_SERVER_URL')
SSL_PORT = 1027
