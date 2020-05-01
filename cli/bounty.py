#   -*- coding: utf-8 -*-
#
#   This file is part of skale-node-cli
#
#   Copyright (C) 2020 SKALE Labs
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
    get_bounty_from_events, get_nodes_for_validator, check_if_validator_is_registered)
from utils.print_formatters import print_bounties
from utils.texts import Texts
from utils.web3_utils import init_skale_from_config

G_TEXTS = Texts()
TEXTS = G_TEXTS['bounty']
MSGS = G_TEXTS['msg']


@click.group()
def bounty_cli():
    pass


@bounty_cli.group('bounty', help=TEXTS['help'])
def bounty():
    pass


@bounty.command(help=TEXTS['validator']['help'])
@click.option(
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
    '--limit', '-l',
    type=int,
    help=MSGS['limit']['help']
)
@click.option(
    '--wei', '-w',
    is_flag=True,
    help=MSGS['wei']['help']
)
def validator(index, since, till, limit, wei):
    if index < 0:
        print(TEXTS['validator']['index']['valid_id_msg'])
        return
    skale = init_skale_from_config()
    if not check_if_validator_is_registered(skale, index):
        print(TEXTS['validator']['index']['id_error_msg'])
        return
    node_ids = get_nodes_for_validator(skale, index)
    if len(node_ids) == 0:
        print(MSGS['no_nodes'])
        return
    print(TEXTS['validator']['index']['wait_msg'])
    bounties, total = get_bounty_from_events(skale, node_ids, since, till, limit, wei)
    if bounties:
        sums = ['Total per period:']
        for i in range(1, len(bounties[0])):
            sums.append(sum([bounty[i] for bounty in bounties]))
        spaces = [''] * len(bounties[0])
        bounties.append(spaces)
        bounties.append(sums)
        print_bounties(node_ids, bounties, wei)
    else:
        print('\n' + MSGS['no_data'])
