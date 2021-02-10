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
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import click

from core.metrics import (
    check_if_node_is_registered, check_if_validator_is_registered, get_metrics_for_node,
    get_metrics_for_validator)
from utils.constants import SPIN_COLOR
from utils.print_formatters import (
    print_node_metrics, print_validator_metrics, print_validator_node_totals)
from utils.texts import Texts
from utils.web3_utils import init_skale_from_config
from yaspin import yaspin

G_TEXTS = Texts()
TEXTS = G_TEXTS['metrics']
MSGS = G_TEXTS['msg']


@click.group()
def metrics_cli():
    pass


@metrics_cli.group('metrics', help=TEXTS['help'])
def metrics():
    pass


@metrics.command(help=TEXTS['node']['help'])
@click.option(
    'node_id',
    '--index', '-id',
    type=int,
    help=TEXTS['node']['index']['help'],
    prompt=TEXTS['node']['index']['prompt']
)
@click.option(
    '--since', '-s',
    type=click.DateTime(formats=['%Y-%m-%d']),
    help=MSGS['since']['help']
)
@click.option(
    '--till', '-t',
    type=click.DateTime(formats=['%Y-%m-%d']),
    help=MSGS['till']['help']
)
@click.option(
    '--wei', '-w',
    is_flag=True,
    help=MSGS['wei']['help']
)
@click.option(
    '--to-file', '-f',
    help=TEXTS['validator']['save_to_file']['help']
)
def node(node_id, since, till, wei, to_file):
    if node_id < 0:
        print(TEXTS['node']['index']['valid_id_msg'])
        return
    skale = init_skale_from_config()
    if not check_if_node_is_registered(skale, node_id):
        print(TEXTS['node']['index']['id_error_msg'])
        return
    with yaspin(text="Loading", color=SPIN_COLOR) as sp:
        sp.text = TEXTS['node']['index']['wait_msg']
        metrics, total_bounty = get_metrics_for_node(skale, int(node_id), since, till, wei, to_file)
    if metrics:
        print_node_metrics(metrics, total_bounty, wei)
    else:
        print(f"\n{MSGS['no_data']}")


@metrics.command(help=TEXTS['validator']['help'])
@click.option(
    'val_id',
    '--index', '-id',
    type=int,
    help=TEXTS['validator']['index']['help'],
    prompt=TEXTS['validator']['index']['prompt']
)
@click.option(
    '--since', '-s',
    type=click.DateTime(formats=['%Y-%m-%d']),
    help=MSGS['since']['help']
)
@click.option(
    '--till', '-t',
    type=click.DateTime(formats=['%Y-%m-%d']),
    help=MSGS['till']['help']
)
@click.option(
    '--wei', '-w',
    is_flag=True,
    help=MSGS['wei']['help']
)
@click.option(
    '--to-file', '-f',
    help=TEXTS['validator']['save_to_file']['help']
)
def validator(val_id, since, till, wei, to_file):
    if val_id < 0:
        print(TEXTS['validator']['index']['valid_id_msg'])
        return
    skale = init_skale_from_config()
    if not check_if_validator_is_registered(skale, val_id):
        print(TEXTS['validator']['index']['id_error_msg'])
        return
    with yaspin(text="Loading", color=SPIN_COLOR) as sp:
        sp.text = TEXTS['validator']['index']['wait_msg']
        metrics, total_bounty = get_metrics_for_validator(skale, val_id, since, till, wei, to_file)
    if metrics['rows']:
        print_validator_metrics(metrics['rows'], wei)
        print_validator_node_totals(metrics['totals'], total_bounty, wei)
    else:
        print('\n' + MSGS['no_data'])
