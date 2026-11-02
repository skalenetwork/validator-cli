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

import datetime
import os

import texttable
from utils.helper import from_wei, permille_to_percent, to_skl


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


def print_validators(validators, wei):
    m_type = 'SKL - wei' if wei else 'SKL'
    headers = [
        'Name',
        'Id',
        'Address',
        'Description',
        'Fee rate (percent %)',
        'Registration time',
        f'Minimum delegation ({m_type})',
        # f'Auto accept',
        'Validator status'
    ]
    rows = []
    for validator in validators:
        dt = datetime.datetime.fromtimestamp(validator['registration_time'])
        strtime = dt.strftime('%d.%m.%Y-%H:%M:%S')
        status = 'Trusted' if validator['trusted'] else 'Registered'
        if not wei:
            validator['minimum_delegation_amount'] = from_wei(
                validator['minimum_delegation_amount'])
        fee_rate_percent = permille_to_percent(validator['fee_rate'])
        rows.append([
            validator['name'],
            validator['id'],
            validator['validator_address'],
            validator['description'],
            fee_rate_percent,
            strtime,
            validator['minimum_delegation_amount'],
            # validator['auto_accept_delegations'],
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
            getattr(delegation['status'], 'name', delegation['status']),
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
        'Balance (ETH)'
    ]
    rows = []
    for address_info in addresses:
        rows.append([
            address_info['address'],
            address_info['status'],
            address_info['balance']
        ])
    print(Formatter().table(headers, rows))


def print_sgx_info(info):
    print(Formatter().table(['KEY', 'VALUE'], [
        ['Server url', info['server_url']],
        ['SSL port', info['ssl_port']],
        ['Address', info['address']],
        ['Key', info['key']]
    ]))


def print_bond_amount(validator_id, bond_amount, wei=False):
    if wei:
        print(f'Bond amount for validator with id '
              f'{validator_id} - {bond_amount} WEI')
    else:
        bond_amount = from_wei(bond_amount)
        print(f'Bond amount for validator with id '
              f'{validator_id} - {bond_amount} SKL')


def print_srw_balance(validator_id, amount, wei=False):
    symbol = 'WEI'
    if not wei:
        symbol = 'ETH'
        amount = from_wei(amount)
    print(f'SRW balance for validator with id {validator_id} - {amount} {symbol}')
