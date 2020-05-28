import sys
from datetime import datetime

from web3.logs import DISCARD

from utils.filter import SkaleFilter
from utils.helper import to_skl

BLOCK_CHUNK_SIZE = 1000


def check_if_node_is_registered(skale, node_id):
    return node_id in skale.nodes_data.get_active_node_ids()


def check_if_validator_is_registered(skale, val_id):
    validator_service = skale.get_contract_by_name('validator_service')
    return validator_service.contract.functions.validatorExists(val_id).call()


def get_nodes_for_validator(skale, val_id):
    validator_service = skale.get_contract_by_name('validator_service')
    return validator_service.contract.functions.getValidatorNodeIndexes(val_id).call()


def get_start_block(skale, node_id):
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
        start_block_number = get_start_block(skale, node_ids[0])
    else:
        start_block_number = find_block_for_tx_stamp(skale, start_date)

    if end_date is None:
        last_block_number = skale.web3.eth.blockNumber
    else:
        last_block_number = find_block_for_tx_stamp(skale, end_date)

    return start_block_number, last_block_number


def format_limit(limit):
    if limit is None:
        return float('inf')
    else:
        return int(limit)


def get_metrics_from_events(skale, node_id, start_date=None, end_date=None,
                            limit=None, wei=None, is_validator=False):
    print(f'node id = {node_id}')
    metrics_rows = []
    total_bounty = 0
    limit = format_limit(limit)

    block_number = skale.monitors_data.contract.functions.getLastBountyBlock(node_id).call()
    while True:
        block_data = skale.web3.eth.getBlock(block_number)
        print(f'block number = {block_number}')
        txs = block_data["transactions"]
        print(txs)
        for tx in txs:
            rec = skale.web3.eth.getTransactionReceipt(tx)
            h_receipt = skale.manager.contract.events.BountyGot().processReceipt(
                rec, errors=DISCARD)
            if len(h_receipt) == 0:
                break
            args = h_receipt[0]['args']
            # print(f'args: {args}')
            print(f"\n >>>>>> previousBlockEvent: {args[f'previousBlockEvent']}")
            block_timestamp = datetime.utcfromtimestamp(block_data['timestamp'])
            bounty = args['bounty']
            if not wei:
                bounty = to_skl(bounty)
            metrics_row = [str(block_timestamp),
                           bounty,
                           args['averageDowntime'],
                           round(args['averageLatency'] / 1000, 1)]
            print(f'metrics = {metrics_row}')
            if is_validator:
                metrics_row.insert(1, args['nodeIndex'])
                total_bounty += metrics_row[2]
            else:
                total_bounty += metrics_row[1]
            metrics_rows.append(metrics_row)

            block_number = args['previousBlockEvent']
        if block_number is None or block_number == 0:
            break
    return metrics_rows, total_bounty


def get_metrics_from_events_old(skale, node_ids, start_date=None, end_date=None,
                                limit=None, wei=None, is_validator=False):
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
            bounty = args['bounty']
            if not wei:
                bounty = to_skl(bounty)
            metrics_row = [str(block_timestamp),
                           bounty,
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


def get_bounty_from_events(skale, node_ids, start_date=None, end_date=None,
                           limit=None, wei=None) -> list:
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
                    bounty_row = bounty_to_ordered_row(cur_month_record, node_ids, wei)
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
        bounty_row = bounty_to_ordered_row(cur_month_record, node_ids, wei)
        total_bounty += bounty_row[1]
        bounty_rows.append(bounty_row)
    return bounty_rows


def bounty_to_ordered_row(cur_month_record, node_ids, wei):
    sum = 0
    bounty_row = []
    key_date = next(iter(cur_month_record))
    bounty_row.append(key_date)

    for node_id in node_ids:
        cur_bounty = cur_month_record[key_date].get(node_id, 0)
        if cur_bounty:
            if not wei:
                cur_bounty = to_skl(cur_bounty)
            sum += cur_bounty
        bounty_row.append(cur_bounty)
    bounty_row.insert(1, sum)
    return bounty_row
