from datetime import datetime
from utils.web3_utils import init_skale_from_config
from utils.filter import SkaleFilter
import sys

BLOCK_CHUNK_SIZE = 1000
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


def progress(count, total, status='', bar_len=60):
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s %s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


def get_start_end_block_numbers(skale, node_ids, start_date=None, end_date=None):
    if start_date is None:
        start_date = datetime.utcfromtimestamp(get_start_date(node_ids[0]))
    else:
        start_date = yy_mm_dd_to_date(start_date)
    if end_date is not None:
        end_date = yy_mm_dd_to_date(end_date)

    start_block_number = find_block_for_tx_stamp(skale, start_date)
    cur_block_number = skale.web3.eth.blockNumber
    last_block_number = find_block_for_tx_stamp(skale, end_date) if end_date is not None \
        else cur_block_number

    return start_block_number, last_block_number


def format_limit(limit):
    if limit is None:
        return float('inf')
    else:
        return int(limit)


def get_metrics_from_events(node_ids, start_date=None, end_date=None,
                            limit=None, is_validator=False):
    skale = init_skale_from_config()
    metrics_rows = []
    total_bounty = 0
    limit = format_limit(limit)
    start_block_number, last_block_number = get_start_end_block_numbers(skale, node_ids,
                                                                        start_date, end_date)
    start_chunk_block_number = start_block_number
    blocks_total = last_block_number - start_block_number
    while len(metrics_rows) < limit:
        progress(start_chunk_block_number - start_block_number, blocks_total)

        end_chunk_block_number = start_chunk_block_number + BLOCK_CHUNK_SIZE - 1
        if end_chunk_block_number > last_block_number:
            end_chunk_block_number = last_block_number

        event_filter = SkaleFilter(
            skale.manager.contract.events.BountyGot,
            from_block=hex(start_chunk_block_number),
            argument_filters={'nodeIndex': node_ids},
            to_block=hex(end_chunk_block_number)
        )
        logs = event_filter.get_events()
        for log in logs:
            args = log['args']
            tx_block_number = log['blockNumber']
            block_data = skale.web3.eth.getBlock(tx_block_number)
            block_timestamp = datetime.utcfromtimestamp(block_data['timestamp'])
            metrics_row = [str(block_timestamp),
                           to_skl(args['bounty']),
                           args['averageDowntime'],
                           round(args['averageLatency'] / 1000, 1)]
            if is_validator:
                metrics_row.insert(1, args['nodeIndex'])
                total_bounty += metrics_row[2]
            else:
                total_bounty += metrics_row[1]
            metrics_rows.append(metrics_row)
            if len(metrics_rows) >= limit:
                break
        start_chunk_block_number = start_chunk_block_number + BLOCK_CHUNK_SIZE
        if end_chunk_block_number >= last_block_number:
            break
    progress(blocks_total, blocks_total)
    return metrics_rows, total_bounty


def get_bounty_from_events(node_ids, start_date=None, end_date=None, limit=None) -> tuple:
    skale = init_skale_from_config()
    bounty_rows = []
    total_bounty = 0
    cur_month_record = {}
    limit = format_limit(limit)
    start_block_number, last_block_number = get_start_end_block_numbers(skale, node_ids,
                                                                        start_date, end_date)
    start_chunk_block_number = start_block_number
    blocks_total = last_block_number - start_block_number

    while len(bounty_rows) < limit:
        progress(start_chunk_block_number - start_block_number, blocks_total)
        end_chunk_block_number = start_chunk_block_number + BLOCK_CHUNK_SIZE - 1
        if end_chunk_block_number > last_block_number:
            end_chunk_block_number = last_block_number

        event_filter = SkaleFilter(
            skale.manager.contract.events.BountyGot,
            from_block=hex(start_chunk_block_number),
            argument_filters={'nodeIndex': node_ids},
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
                             f'{block_timestamp.strftime("%d")}'
            if cur_year_month in cur_month_record:
                if node_id in cur_month_record[cur_year_month]:
                    cur_month_record[cur_year_month][node_id] += bounty
                else:
                    cur_month_record[cur_year_month][node_id] = bounty
            else:
                if bool(cur_month_record):  # if dict is not empty
                    bounty_row = bounty_to_ordered_row(cur_month_record, node_ids)
                    total_bounty += bounty_row[1]
                    bounty_rows.append(bounty_row)
                cur_month_record = {cur_year_month: {node_id: bounty}}
            if len(bounty_rows) >= limit:
                break
        start_chunk_block_number = start_chunk_block_number + BLOCK_CHUNK_SIZE
        if end_chunk_block_number >= last_block_number:
            break
    progress(blocks_total, blocks_total)
    if bool(cur_month_record) and len(bounty_rows) < limit:
        bounty_row = bounty_to_ordered_row(cur_month_record, node_ids)
        total_bounty += bounty_row[1]
        bounty_rows.append(bounty_row)
    return bounty_rows, total_bounty


def to_skl(digits):
    return digits / (10 ** 18)


def bounty_to_ordered_row(cur_month_record, node_ids):
    sum = 0
    bounty_row = []
    key_date = next(iter(cur_month_record))
    bounty_row.append(key_date)

    for node_id in node_ids:
        cur_bounty = cur_month_record[key_date].get(node_id, 0)
        if cur_bounty:
            cur_bounty = to_skl(cur_bounty)
            sum += cur_bounty
        bounty_row.append(cur_bounty)
    bounty_row.insert(1, sum)
    return bounty_row
