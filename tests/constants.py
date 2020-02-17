import os


HERE = os.path.dirname(os.path.realpath(__file__))
TEST_PK_FILE = os.path.join(HERE, 'test-pk.txt')
SECOND_TEST_PK_FILE = os.path.join(HERE, 'second-test-pk.txt')

# validator

D_VALIDATOR_ID = 1
D_VALIDATOR_NAME = 'test'
D_VALIDATOR_DESC = 'test'
D_VALIDATOR_FEE = 10
D_VALIDATOR_MIN_DEL = 1000

D_DELEGATION_ID = 0
D_DELEGATION_AMOUNT = 55000000
D_DELEGATION_PERIOD = 3
D_DELEGATION_INFO = 'test'
