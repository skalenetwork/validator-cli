from datetime import datetime
from utils.web3_utils import init_skale_from_config
from utils.filter import SkaleFilter


BLOCK_STEP = 1000
FILTER_PERIOD = 12


def get_start_date(node_id):
    skale = init_skale_from_config()
    return skale.nodes_data.get(node_id)['start_date']


def get_last_reward_date(node_id):
    skale = init_skale_from_config()
    return skale.nodes_data.get(node_id)['last_reward_date']


def find_block_for_tx_stamp(skale, tx_stamp, lo=0, hi=None):
    if hi is None:
        hi = skale.web3.eth.blockNumber
    while lo < hi:
        mid = (lo + hi) // 2
        block_data = skale.web3.eth.getBlock(mid)
        midval = datetime.utcfromtimestamp(block_data['timestamp'])
        if midval < tx_stamp:
            lo = mid + 1
        elif midval > tx_stamp:
            hi = mid
        else:
            return mid
    return lo - 1


def get_bounty_from_events(node_id, start_date=None, end_date=None, is_limited=True):
    skale = init_skale_from_config()
    bounties = []
    start_block_number = find_block_for_tx_stamp(skale, start_date)
    cur_block_number = skale.web3.eth.blockNumber
    last_block_number = find_block_for_tx_stamp(skale, end_date) if end_date is not None \
        else cur_block_number
    while not is_limited or len(bounties) < FILTER_PERIOD:
        end_chunk_block_number = start_block_number + BLOCK_STEP - 1
        if end_chunk_block_number > last_block_number:
            end_chunk_block_number = last_block_number

        event_filter = SkaleFilter(
            skale.manager.contract.events.BountyGot,
            from_block=hex(start_block_number),
            argument_filters={'nodeIndex': node_id},
            to_block=hex(end_chunk_block_number)
        )
        logs = event_filter.get_events()

        for log in logs:
            args = log['args']

            tx_block_number = log['blockNumber']
            block_data = skale.web3.eth.getBlock(tx_block_number)
            block_timestamp = str(datetime.utcfromtimestamp(block_data['timestamp']))
            bounties.append([
                block_timestamp,
                args['bounty'],
                args['averageDowntime'],
                round(args['averageLatency'] / 1000, 1)
            ])
            if is_limited and len(bounties) >= FILTER_PERIOD:
                break
        start_block_number = start_block_number + BLOCK_STEP
        if end_chunk_block_number >= last_block_number:
            break
    return bounties


def get_all_bounties(node_id):
    node_start_date = datetime.utcfromtimestamp(get_start_date(node_id))
    bounties_list = get_bounty_from_events(node_id, node_start_date, is_limited=False)
    return {'bounties': bounties_list}

