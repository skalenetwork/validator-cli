#   -*- coding: utf-8 -*-
#
#   This file is part of validator-cli
#
#   Copyright (C) 2019 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import threading
from datetime import datetime

from web3.logs import DISCARD

import pandas as pd
from utils.helper import to_skl

BLOCK_CHUNK_SIZE = 1000


def check_if_node_is_registered(skale, node_id):
    nodes_number = skale.nodes.contract.functions.getNumberOfNodes().call()
    return node_id in range(0, nodes_number)


def check_if_validator_is_registered(skale, val_id):
    return skale.validator_service.validator_exists(val_id)


def get_nodes_for_validator(skale, val_id):
    return skale.nodes.get_validator_node_indices(val_id)


def get_metrics_for_validator(skale, val_id, start_date=None, end_date=None, wei=None,
                              to_file=None):
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
            df.to_csv(to_file, index=False)
    else:
        metrics_rows = metrics_sums = total_bounty = None
    return {'rows': metrics_rows, 'totals': metrics_sums}, total_bounty


def get_metrics_for_node(skale, node_id, start_date=None, end_date=None, wei=None, to_file=None):
    metrics = get_metrics_from_events(skale, node_id, start_date, end_date)
    columns = ['Date', 'Bounty', 'Downtime', 'Latency']
    df = pd.DataFrame(metrics, columns=columns)
    if not wei:
        df['Bounty'] = df['Bounty'].apply(to_skl)
    total_bounty = df['Bounty'].sum()
    metrics_rows = df.values.tolist()
    if to_file:
        df.to_csv(to_file, index=False)
    print(f'debug in core: {metrics_rows}')
    return metrics_rows, total_bounty


def get_metrics_from_events(skale, node_id, start_date=None, end_date=None,
                            is_validator=False):
    metrics_rows = []

    block_number = skale.monitors.get_last_bounty_block(node_id)
    while True:
        block_data = skale.web3.eth.getBlock(block_number)
        txs = block_data["transactions"]
        for tx in txs:
            rec = skale.web3.eth.getTransactionReceipt(tx)
            if rec["to"] != skale.manager.contract.address:
                continue
            h_receipt = skale.manager.contract.events.BountyReceived().processReceipt(
                rec, errors=DISCARD)
            if len(h_receipt) == 0:
                continue
            args = h_receipt[0]['args']
            block_timestamp = datetime.utcfromtimestamp(block_data['timestamp'])
            if start_date is not None and start_date > block_timestamp:
                return metrics_rows
            if args['nodeIndex'] == node_id:
                block_number = args['previousBlockEvent']
                if end_date is not None and end_date <= block_timestamp:
                    break
                bounty = args['bounty']
                metrics_row = [str(block_timestamp),
                               bounty,
                               args['averageDowntime'],
                               round(args['averageLatency'] / 1000, 1)]
                if is_validator:
                    metrics_row.insert(1, args['nodeIndex'])
                metrics_rows.append(metrics_row)
                break

        if block_number is None or block_number == 0:
            break
    return metrics_rows
