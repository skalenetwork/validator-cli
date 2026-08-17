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
import re
from setuptools import find_packages, setup


def read(*parts):
    path = os.path.join(os.path.dirname(__file__), *parts)
    f = open(path, "r")
    return f.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Couldn't parse version from file.")


extras_require = {
    'linter': [
        "flake8==7.3.0",
        "isort==8.0.1",
    ],
    'dev': [
        "PyInstaller==6.22.1",
        "pytest==9.1.1",
        "twine==7.0.0",
        "mock==5.2.0",
        "boto3==1.43.72",
        "pytest-cov==7.1.0",
        "codecov==2.1.13"
    ],
    'hw-wallet': [
        "ledgerblue==0.1.58"
    ]
}

extras_require['dev'] = (
    extras_require['linter'] + extras_require['dev'] + extras_require['hw-wallet']
)


setup(
    name='validator-cli',
    # *IMPORTANT*: Don't manually change the version here.
    # Use the 'bumpversion' utility instead.
    version=find_version("cli", "__init__.py"),
    include_package_data=True,
    description='SKALE validator tools',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='SKALE Labs',
    author_email='support@skalelabs.com',
    url='https://github.com/skalenetwork/validator-cli',
    install_requires=[
        "click==8.4.2",
        "skale.py==7.92dev0",
        "skale-contracts==2.0.0a10",
        "sgx-py==0.11dev0",
        "web3==7.14.0",
        "hexbytes==1.3.1",
        "yaspin==3.4.0",
        "PyYAML==6.0.3",
        "texttable==1.7.0",
        "pandas==3.0.5",
        "terminaltables==3.1.10",
        "wcwidth==0.8.2",
    ],
    python_requires='>=3.11,<4',
    extras_require=extras_require,

    keywords=['skale', 'cli'],
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 (AGPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.14',
    ],
)
