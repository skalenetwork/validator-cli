from datetime import datetime
from utils.web3_utils import init_skale_from_config
from utils.filter import SkaleFilter


BLOCK_STEP = 1000
FILTER_PERIOD = 12


def get_nodes_for_validator(val_id):
    return ['20', '12', '18', '13', '15']  # TODO: Return test array. Implement later


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


def yy_mm_dd_to_date(date_str):
    format_str = '%y-%m-%d'
    return datetime.strptime(date_str, format_str)


def get_bounty_from_events(nodes, start_date=None, end_date=None,
                           is_validator=False, is_limited=False):
    skale = init_skale_from_config()
    metrics = []
    bounties = []
    cur_month_record = {}
    if start_date is None:
        start_date = datetime.utcfromtimestamp(get_start_date(nodes[0]))
    else:
        start_date = yy_mm_dd_to_date(start_date)
    if end_date is not None:
        end_date = yy_mm_dd_to_date(end_date)

    start_block_number = find_block_for_tx_stamp(skale, start_date)
    cur_block_number = skale.web3.eth.blockNumber
    last_block_number = find_block_for_tx_stamp(skale, end_date) if end_date is not None \
        else cur_block_number
    while not is_limited or len(metrics) < FILTER_PERIOD:
        end_chunk_block_number = start_block_number + BLOCK_STEP - 1
        if end_chunk_block_number > last_block_number:
            end_chunk_block_number = last_block_number

        event_filter = SkaleFilter(
            skale.manager.contract.events.BountyGot,
            from_block=hex(start_block_number),
            argument_filters={'nodeIndex': nodes},
            to_block=hex(end_chunk_block_number)
        )
        logs = event_filter.get_events()

        for log in logs:
            args = log['args']
            node_id = args['nodeIndex']
            bounty = args['bounty']
            tx_block_number = log['blockNumber']
            block_data = skale.web3.eth.getBlock(tx_block_number)
            block_timestamp = datetime.utcfromtimestamp(block_data['timestamp'])
            cur_year_month = f'{block_timestamp.strftime("%Y")} {block_timestamp.strftime("%B")}'
            # for tests where epoch = 1 hour
            cur_year_month = f'{cur_year_month} ' \
                             f'{block_timestamp.strftime("%d")}-{block_timestamp.strftime("%H")}'
            if is_validator:
                if cur_year_month in cur_month_record:
                    if node_id in cur_month_record[cur_year_month]:
                        cur_month_record[cur_year_month][node_id] += bounty
                    else:
                        cur_month_record[cur_year_month][node_id] = bounty
                else:
                    if cur_month_record != {}:
                        bounties.append(cur_month_record)
                    cur_month_record = {cur_year_month: {node_id: bounty}}
                # metrics.append([
                #     str(block_timestamp),
                #     args['nodeIndex'],
                #     args['bounty'],
                #     args['averageDowntime'],
                #     round(args['averageLatency'] / 1000, 1)
                # ])
            else:
                metrics.append([
                    str(block_timestamp),
                    args['bounty'],
                    args['averageDowntime'],
                    round(args['averageLatency'] / 1000, 1)
                ])

            if is_limited and len(metrics) >= FILTER_PERIOD:
                break
        start_block_number = start_block_number + BLOCK_STEP
        if end_chunk_block_number >= last_block_number:
            break
    if cur_month_record != {}:
        bounties.append(cur_month_record)
    # return {'metrics': metrics}
    return bounties


def get_bounty_rows(nodes, bounties):
    rows = []

    for object in bounties:
        node_bounties = []
        key = next(iter(object))
        node_bounties.append(key)
        for node in nodes:
            node_bounties.append(object[key].get(node, ''))
        rows.append(node_bounties)
    return rows


if __name__ == '__main__':
    # For tests
    date = yy_mm_dd_to_date('20-12-11')
    nodes = get_nodes_for_validator(id)
    print('Please wait - collecting metrics from blockchain...')
    nodes = [int(node) for node in nodes]
    bounties = get_bounty_from_events(nodes, '20-01-27', '20-01-28', is_validator=True)
    for b in bounties:
        print(b)
