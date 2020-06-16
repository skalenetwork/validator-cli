#   -*- coding: utf-8 -*-
#
#   This file is part of validator-cli
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
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import datetime
import texttable

from terminaltables import SingleTable
from utils.helper import to_skl, from_wei


def get_tty_width():
    tty_size = os.popen('stty size 2> /dev/null', 'r').read().split()
    if len(tty_size) != 2:
        return 0
    _, width = tty_size
    return int(width)


class Formatter(object):
    def table(self, headers, rows):
        table = texttable.Texttable(max_width=get_tty_width())
        table.set_cols_dtype(['t' for h in headers])
        table.add_rows([headers] + rows)
        table.set_deco(table.HEADER)
        table.set_chars(['-', '|', '+', '-'])

        return table.draw()


def format_date(date):
    return date.strftime("%b %d %Y %H:%M:%S")


def print_validators(validators, wei):
    m_type = 'SKL - wei' if wei else 'SKL'
    headers = [
        'Name',
        'Id',
        'Address',
        'Description',
        'Fee rate (permille)',
        'Registration time',
        f'Minimum delegation ({m_type})',
        'Validator status'
    ]
    rows = []
    for validator in validators:
        date = datetime.datetime.fromtimestamp(validator['registration_time'])
        status = 'Trusted' if validator['trusted'] else 'Registered'
        if not wei:
            validator['minimum_delegation_amount'] = from_wei(
                validator['minimum_delegation_amount'])
        rows.append([
            validator['name'],
            validator['id'],
            validator['validator_address'],
            validator['description'],
            validator['fee_rate'],
            date,
            validator['minimum_delegation_amount'],
            status
        ])
    print(Formatter().table(headers, rows))


def print_delegations(delegations: list, wei: bool) -> None:
    amount_header = 'Amount (wei)' if wei else 'Amount (SKL)'
    headers = [
        'Id',
        'Delegator Address',
        'Status',
        'Validator Id',
        amount_header,
        'Delegation period (months)',
        'Created At',
        'Info'
    ]
    rows = []
    for delegation in delegations:
        date = datetime.datetime.fromtimestamp(delegation['created'])
        amount = delegation['amount'] if wei else to_skl(delegation['amount'])
        rows.append([
            delegation['id'],
            delegation['address'],
            delegation['status'],
            delegation['validator_id'],
            amount,
            delegation['delegation_period'],
            date,
            delegation['info']
        ])
    print(Formatter().table(headers, rows))


def print_linked_addresses(addresses):
    headers = [
        'Address',
        'Status',
        'Balance (ETH)',
        'Nodes'
    ]
    rows = []
    for address_info in addresses:
        rows.append([
            address_info['address'],
            address_info['status'],
            address_info['balance'],
            address_info['nodes'],
        ])
    print(Formatter().table(headers, rows))


def print_node_metrics(rows, total, wei):
    headers = [
        'Date',
        'Bounty',
        'Downtime',
        'Latency'
    ]
    table = texttable.Texttable(max_width=get_tty_width())
    table.set_cols_align(["l", "r", "r", "r"])
    if wei:
        table.set_cols_dtype(["t", "i", "i", "f"])
    else:
        table.set_cols_dtype(["t", "a", "i", "f"])
    table.set_precision(1)
    table.add_rows([headers] + rows)
    table.set_deco(table.HEADER)
    table.set_chars(['-', '|', '+', '-'])
    print('\n')
    print(table.draw())
    print_total_info(total, wei)


def print_validator_metrics(rows, total, wei):
    headers = [
        'Date',
        'Node ID',
        'Bounty',
        'Downtime',
        'Latency'
    ]
    table = texttable.Texttable(max_width=get_tty_width())
    table.set_cols_align(["l", "r", "r", "r", "r"])
    if wei:
        table.set_cols_dtype(["t", "i", "i", "i", "f"])
    else:
        table.set_cols_dtype(["t", "i", "f", "i", "f"])
    table.set_precision(1)
    table.add_rows([headers] + rows)
    table.set_deco(table.HEADER)
    table.set_chars(['-', '|', '+', '-'])
    print('\n')
    print(table.draw())
    print_total_info(total, wei)


def print_bounties(nodes, bounties, wei):
    headers = ['Date', 'All nodes']
    node_headers = [f'Node ID = {node}' for node in nodes]
    headers.extend(node_headers)
    table = texttable.Texttable(max_width=get_tty_width())
    format_string = ['t']
    if wei:
        format_string.extend(['t' for h in range(len(headers) - 1)])
    else:
        format_string.extend(['f' for h in range(len(headers) - 1)])
        table.set_precision(3)
    table.set_cols_dtype(format_string)
    table.set_cols_align(['r' for h in headers])
    table.add_rows([headers] + bounties)
    table.set_deco(table.HEADER)
    table.set_chars(['-', '|', '+', '-'])
    print('\n')
    print(table.draw())


def print_total_info(total, wei):
    if wei:
        total_string = f'Total bounty per the given period: {total:} wei'
    else:
        total_string = f'Total bounty per the given period: {total:.3f} SKL'
    print('\n', total_string)


def print_sgx_info(info):
    table_data = [
        ('KEY', 'VALUE'),
        ('Server url', info['server_url']),
        ('SSL port', info['ssl_port']),
        ('Address', info['address']),
        ('Key', info['key'])
    ]
    table = SingleTable(table_data)
    print(table.table)


def print_bond_amount(validator_id, bond_amount, wei=False):
    if wei:
        print(f'Bond amount for validator with id '
              f'{validator_id} - {bond_amount} WEI')
    else:
        bond_amount = from_wei(bond_amount)
        print(f'Bond amount for validator with id '
              f'{validator_id} - {bond_amount} SKL')
