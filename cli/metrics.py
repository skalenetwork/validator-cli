#   -*- coding: utf-8 -*-
#
#   This file is part of skale-node-cli
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
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import click
from core.metrics import get_metrics_from_events, get_nodes_for_validator
from utils.print_formatters import print_node_metrics, print_validator_metrics


@click.group()
def metrics_cli():
    pass


@metrics_cli.group('metrics', help="Node metrics commands")
def metrics():
    pass


@metrics.command(help="List of bounties and metrics for node with given id")
@click.option('--index', '-id')
@click.option('--since', '-s')
@click.option('--till', '-t')
@click.option('--limit', '-l')
def node(index, since, till, limit):
    if index is None:
        print('Node ID expected: "metrics node -id N"')
        return
    print('Please wait - collecting metrics from blockchain...')
    metrics, total_bounty = get_metrics_from_events([int(index)], since, till, limit)
    print_node_metrics(metrics, total_bounty)


@metrics.command(help="List of bounties and metrics for validator with given id")
@click.option('--index', '-id')
@click.option('--since', '-s')
@click.option('--till', '-t')
@click.option('--limit', '-l')
def validator(index, since, till, limit):
    if index is None:
        print('Validator ID expected: "metrics node -id N"')
        return
    nodes_ids = get_nodes_for_validator(index)
    print('Please wait - collecting metrics from blockchain...')
    nodes = [int(node_id) for node_id in nodes_ids]
    metrics, total_bounty = get_metrics_from_events(nodes, since, till, limit, is_validator=True)
    print_validator_metrics(metrics, total_bounty)
