from datetime import datetime

from web3.logs import DISCARD

import pandas as pd
import threading

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


def get_metrics_for_validator(skale, val_id, start_date=None, end_date=None, wei=None,
                              to_file=False):
    class nodeThread(threading.Thread):
        def __init__(self, node_id):
            threading.Thread.__init__(self)
            self.node_id = node_id

        def run(self):
            metrics = get_metrics_from_events(skale, self.node_id, start_date, end_date,
                                              is_validator=True)
            all_metrics.extend(metrics)

    node_ids = get_nodes_for_validator(skale, val_id, )
    all_metrics = []
    thread_list = []
    for node_id in node_ids:
        node_thread = nodeThread(node_id)

        thread_list.append(node_thread)
        node_thread.start()
    for th in thread_list:
        th.join()
    if all_metrics:
        columns = ['Date', 'Node ID', 'Bounty', 'Downtime', 'Latency']
        df = pd.DataFrame(all_metrics, columns=columns)
        if not wei:
            df['Bounty'] = df['Bounty'].apply(to_skl)
        df.sort_values(by=['Date'], inplace=True, ascending=False)
        metrics_rows = df.values.tolist()
        node_group = df.groupby(['Node ID'])
        metrics_sums = node_group.agg({'Bounty': 'sum', 'Downtime': 'sum', 'Latency': 'mean'})
        metrics_sums = metrics_sums.reset_index().values.tolist()
        total_bounty = df['Bounty'].sum()
        if to_file:
            df.to_csv('metrics.csv', index=False)
    else:
        metrics_rows = metrics_sums = total_bounty = None
    return {'rows': metrics_rows, 'totals': metrics_sums}, total_bounty


def get_metrics_for_node(skale, node_id, start_date=None, end_date=None, wei=None, to_file=False):
    metrics = get_metrics_from_events(skale, node_id, start_date, end_date)
    columns = ['Date', 'Bounty', 'Downtime', 'Latency']
    df = pd.DataFrame(metrics, columns=columns)
    if not wei:
        df['Bounty'] = df['Bounty'].apply(to_skl)
    total_bounty = df['Bounty'].sum()
    metrics_rows = df.values.tolist()
    if to_file:
        df.to_csv('node_metrics.csv', index=False)
    return metrics_rows, total_bounty


def get_metrics_from_events(skale, node_id, start_date=None, end_date=None,
                            is_validator=False):
    metrics_rows = []

    block_number = skale.monitors_data.contract.functions.getLastBountyBlock(node_id).call()
    while True:
        block_data = skale.web3.eth.getBlock(block_number)
        txs = block_data["transactions"]
        for tx in txs:
            rec = skale.web3.eth.getTransactionReceipt(tx)
            h_receipt = skale.manager.contract.events.BountyGot().processReceipt(
                rec, errors=DISCARD)
            if len(h_receipt) == 0:
                continue
            args = h_receipt[0]['args']
            block_timestamp = datetime.utcfromtimestamp(block_data['timestamp'])
            if start_date is not None and start_date > block_timestamp:
                return metrics_rows
            if end_date is None or end_date > block_timestamp:
                bounty = args['bounty']
                metrics_row = [str(block_timestamp),
                               bounty,
                               args['averageDowntime'],
                               round(args['averageLatency'] / 1000, 1)]
                if is_validator:
                    metrics_row.insert(1, args['nodeIndex'])
                metrics_rows.append(metrics_row)
            block_number = args['previousBlockEvent']

        if block_number is None or block_number == 0:
            break
    return metrics_rows
