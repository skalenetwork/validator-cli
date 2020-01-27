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

from urllib.parse import urlparse

import click
from web3.auto import w3


class EthAddressType(click.ParamType):
    name = 'eth_address'

    def convert(self, value, param, ctx):
        if w3.isAddress(value):
            return value
        else:
            self.fail(f'Wrong Ethereum address provided: {value}', param, ctx)


class PercentageType(click.ParamType):
    name = 'percentage'

    def convert(self, value, param, ctx):
        if 0 <= float(value) <= 100:
            return value
        else:
            self.fail(
                f'Wrong percentage value provided: {value}, should be in range(0, 100)',
                param,
                ctx
            )


class UrlType(click.ParamType):
    name = 'url'

    def convert(self, value, param, ctx):
        try:
            result = urlparse(value)
        except ValueError:
            self.fail(f'Some characters are not allowed in {value}',
                      param, ctx)
        if not all([result.scheme, result.netloc]):
            self.fail(f'Expected valid url. Got {value}', param, ctx)
        return value
