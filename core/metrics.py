from datetime import datetime
from utils.web3_utils import init_skale_from_config
from utils.filter import SkaleFilter
import sys

BLOCK_CHUNK_SIZE = 1000


def get_nodes_for_validator(val_id):
    skale = init_skale_from_config()
    validator_service = skale.get_contract_by_name('validator_service')
    return validator_service.contract.functions.getValidatorNodeIndexes(val_id).call()


def get_start_block(node_id):
    skale = init_skale_from_config()
    return skale.nodes_data.get(node_id)['start_block']


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


def progress_bar(count, total, status='', bar_len=60):
    if total > 0:
        done_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '=' * done_len + '-' * (bar_len - done_len)

        sys.stdout.write('[%s] %s%s %s\r' % (bar, percents, '%', status))
        sys.stdout.flush()


def get_start_end_block_numbers(skale, node_ids, start_date=None, end_date=None):
    if start_date is None:
        start_block_number = get_start_block(node_ids[0])
    else:
        start_block_number = find_block_for_tx_stamp(skale, start_date)

    if start_date is None:
        last_block_number = skale.web3.eth.blockNumber
    else:
        last_block_number = find_block_for_tx_stamp(skale, end_date)

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
        progress_bar(start_chunk_block_number - start_block_number, blocks_total)

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
    progress_bar(blocks_total, blocks_total)
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
        progress_bar(start_chunk_block_number - start_block_number, blocks_total)
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
                if bool(cur_month_record):  # if prepared dict is not empty
                    bounty_row = bounty_to_ordered_row(cur_month_record, node_ids)
                    total_bounty += bounty_row[1]
                    bounty_rows.append(bounty_row)
                cur_month_record = {cur_year_month: {node_id: bounty}}
            if len(bounty_rows) >= limit:
                break
        start_chunk_block_number = start_chunk_block_number + BLOCK_CHUNK_SIZE
        if end_chunk_block_number >= last_block_number:
            break
    progress_bar(blocks_total, blocks_total)
    if bool(cur_month_record) and len(bounty_rows) < limit:
        bounty_row = bounty_to_ordered_row(cur_month_record, node_ids)
        total_bounty += bounty_row[1]
        bounty_rows.append(bounty_row)
    return bounty_rows, total_bounty


def to_skl(digits):  # convert to SKL
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
