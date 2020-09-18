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

import os
import json

from utils.constants import SKALE_VAL_LEDGER_INFO_FILE


def get_ledger_wallet_info() -> dict:
    if not os.path.isfile(SKALE_VAL_LEDGER_INFO_FILE):
        return {}
    with open(SKALE_VAL_LEDGER_INFO_FILE) as info_file:
        return json.load(info_file)


def save_ledger_wallet_info(address_index, keys_type):
    with open(SKALE_VAL_LEDGER_INFO_FILE, 'w') as info_file:
        data_to_dump = {
            'address_index': address_index,
            'keys_type': keys_type,
        }
        json.dump(data_to_dump, info_file)
