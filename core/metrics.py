import threading
import sys
from datetime import datetime

from web3.logs import DISCARD

import pandas as pd
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


def get_metrics_for_validator2(skale, val_id, start_date=None, end_date=None, wei=None,
                               to_file=False):
    node_ids = get_nodes_for_validator(skale, val_id, )
    all_metrics = []
    total_bounty = 0
    for node_id in node_ids:
        metrics, total_bounty = get_metrics_from_events(skale, node_id, start_date, end_date, wei,
                                                        is_validator=True)
        all_metrics.extend(metrics)
        total_bounty += total_bounty
    columns = ['Date', 'Node ID', 'Bounty', 'Downtime', 'Latency']
    df = pd.DataFrame(all_metrics, columns=columns)
    df.sort_values(by=['Date'], inplace=True, ascending=False)
    metrics_rows = df.values.tolist()
    if to_file:
        df.to_csv('metrics.csv', index=False)
    node_group = df.groupby(['Node ID'])
    metrics_sums = node_group.agg({'Bounty': 'sum', 'Downtime': 'sum', 'Latency': 'mean'})
    # print(metrics_sums)
    return {'rows': metrics_rows, 'totals': metrics_sums}, total_bounty


def get_metrics_for_validator(skale, val_id, start_date=None, end_date=None, wei=None,
                              to_file=False):
    class nodeThread(threading.Thread):
        def __init__(self, node_id):
            threading.Thread.__init__(self)
            self.node_id = node_id

        def run(self):
            # print("Starting ", self.node_id)
            metrics = get_metrics_from_events(skale, self.node_id, start_date, end_date, wei,
                                              is_validator=True)
            all_metrics.extend(metrics)
            # print("Exiting :", self.node_id)

    node_ids = get_nodes_for_validator(skale, val_id, )
    # print(f'<<<<<<< nodes: {node_ids}')
    # print(skale.nodes_data.get_active_node_ids())
    all_metrics = []
    thread_list = []
    for node_id in node_ids:
        node_thread = nodeThread(node_id)

        thread_list.append(node_thread)
        node_thread.start()
    for th in thread_list:
        th.join()
    # print(f'>>>> ALL: {all_metrics}')
    if all_metrics:
        columns = ['Date', 'Node ID', 'Bounty', 'Downtime', 'Latency']
        df = pd.DataFrame(all_metrics, columns=columns)
        df.sort_values(by=['Date'], inplace=True, ascending=False)
        metrics_rows = df.values.tolist()
        node_group = df.groupby(['Node ID'])
        metrics_sums = node_group.agg({'Bounty': 'sum', 'Downtime': 'sum', 'Latency': 'mean'}).reset_index()
        metrics_sums = metrics_sums.values.tolist()
        total_bounty = df['Bounty'].sum()
        if to_file:
            df.to_csv('metrics.csv', index=False)
    else:
        metrics_rows = metrics_sums = total_bounty = None
    return {'rows': metrics_rows, 'totals': metrics_sums}, total_bounty


def get_metrics_for_node(skale, node_id, start_date=None, end_date=None, wei=None, to_file=False):
    metrics = get_metrics_from_events(skale, node_id, start_date, end_date, wei)
    columns = ['Date', 'Bounty', 'Downtime', 'Latency']
    df = pd.DataFrame(metrics, columns=columns)
    total_bounty = df['Bounty'].sum()
    if to_file:
        df.to_csv('node_metrics.csv', index=False)
    return metrics, total_bounty


def get_metrics_from_events(skale, node_id, start_date=None, end_date=None,
                            wei=None, is_validator=False):
    metrics_rows = []

    block_number = skale.monitors_data.contract.functions.getLastBountyBlock(node_id).call()
    while True:
        block_data = skale.web3.eth.getBlock(block_number)
        # print(f'block number = {block_number}')
        txs = block_data["transactions"]
        for tx in txs:
            rec = skale.web3.eth.getTransactionReceipt(tx)
            h_receipt = skale.manager.contract.events.BountyGot().processReceipt(
                rec, errors=DISCARD)
            if len(h_receipt) == 0:
                continue
            args = h_receipt[0]['args']
            block_timestamp = datetime.utcfromtimestamp(block_data['timestamp'])
            # print(start_date, end_date, block_timestamp)
            if start_date is not None and start_date > block_timestamp:
                return metrics_rows
            if end_date is None or end_date > block_timestamp:
                bounty = args['bounty']
                if not wei:
                    bounty = to_skl(bounty)
                metrics_row = [str(block_timestamp),
                               bounty,
                               args['averageDowntime'],
                               round(args['averageLatency'] / 1000, 1)]
                if is_validator:
                    metrics_row.insert(1, args['nodeIndex'])
                metrics_rows.append(metrics_row)
                # print(f'metrics = {metrics_rows}')
            block_number = args['previousBlockEvent']

        if block_number is None or block_number == 0:
            break
    return metrics_rows
