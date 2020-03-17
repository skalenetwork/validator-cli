# SKALE Validator CLI

[![Build Status](https://travis-ci.com/skalenetwork/validator-cli.svg?token=tLesVRTSHvWZxoyqXdoA&branch=develop)](https://travis-ci.com/skalenetwork/validator-cli)
[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

## Table of Contents

1.  [Installation](#installation)
2.  [CLI usage](#cli-usage)  
    2.1 [Init](#init)  
    2.2 [Validator commands](#validator-commands)  
    2.3 [Holder commands](#holder-commands)
3.  [Development](#development)  

## Installation

### Requirements

-   Linux x86_64 machine

-   Download executable

```bash
VERSION_NUM=0.1.0-develop.3 && sudo -E bash -c "curl -L https://validator-cli.sfo2.digitaloceanspaces.com/develop/sk-val-$VERSION_NUM-`uname -s`-`uname -m` >  /usr/local/bin/sk-val"
```

-   Apply executable permissions to the binary:

```bash
chmod +x /usr/local/bin/sk-val
```

## CLI Usage

### Init

Download SKALE Manager contracts info and set the endpoint.

```bash
sk-val init
```

Required arguments:

-   `--endpoint/-e` - RPC endpoint of the node in the network where SKALE manager is deployed (`ws` or `wss`)
-   `--contracts-url/-c` - - URL to SKALE Manager contracts ABI and addresses
-   `-w/--wallet` - Type of the wallet that will be used for signing transactions (software or ledger)

Usage example:

```bash
sk-val init -e ws://geth.test.com:8546 -c https://test.com/manager.json --wallet-type software
```

### Validator commands

#### Register

Register as a new SKALE validator

```bash
sk-val validator register
```

Required arguments:

-   `--name/-n` - Validator name
-   `--description/-d` - Validator description
-   `--commission-rate/-c` - Commission rate (percentage)
-   `--min-delegation` - Validator minimum delegation amount

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)
-   `--yes` - Confirmation flag

Usage example:

```bash
sk-val register -n test -d "test description" -c 20 --min-delegation 1000 --pk-file ./pk.txt
```

#### List

List of available validators

```bash
sk-val validator ls
```

#### Delegations

List of delegations for address

```bash
sk-val validator delegations [ADDRESS]
```

Required params:

1) Address - Ethereum address of the validator

#### Accept pending delegation

Accept pending delegation request by delegation ID

```bash
sk-val validator accept-delegation --pk-file ./pk.txt
```

Required arguments:

-   `--delegation-id` - ID of the delegation request to accept

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)
-   `--yes` - Confirmation flag

#### Validator linked addresses

List of the linked addresses for validator address

```bash
sk-val validator linked-addresses [ADDRESS]
```

Required params:

1) Address - Ethereum address of the validator

#### Link address

Link node address to the validator account

```bash
sk-val validator link-address [ADDRESS] --pk-file ./pk.txt
```

Required params:

1) Address - Ethereum address that will be linked

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)
-   `--yes` - Confirmation flag

#### Unlink address

Unlink node address from the validator account

```bash
sk-val validator unlink-address [ADDRESS] --pk-file ./pk.txt
```

Required params:

1) Address - Ethereum address that will be unlinked

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)
-   `--yes` - Confirmation flag

#### Validator info

Info about the validator

```bash
sk-val validator info [VALIDATOR_ID]
```

Required params:

1) Address - Ethereum address of the validator

Output info:

1) Validator ID
2) Name
3) Address
4) Fee rate (%)
5) Minimum delegation amount (SKL)
6) Delegated tokens
7) Earned bounty
8) MSR

### Holder commands

#### Delegate

Delegate tokens to validator

```bash
sk-val holder delegate
```

Required arguments:

-   `--validator-id` - ID of the validator to delegate
-   `--amount` - Amount of SKALE tokens to delegate
-   `--delegation-period` - Delegation period (in months)
-   `--info` - Delegation request info

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)

#### Delegations

List of delegations for address

```bash
sk-val holder delegations [ADDRESS]
```

Required params:

1) Address - Ethereum address of the token holder

#### Cancel pending delegation

Cancel pending delegation request

```bash
sk-val holder cancel-delegation [DELEGATION_ID]
```

Required params:

1) Delegation ID - ID of the delegation to cancel

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)

## Development

### Setup repo

#### Install development dependencies

```bash
pip install -e .[dev]
```

##### Add flake8 git hook

In file `.git/hooks/pre-commit` add:

```bash
#!/bin/sh
flake8 .
```

### Debugging

Run commands in dev mode:

```bash
python main.py YOUR_COMMAND
```

### Setting up Travis

Required environment variables:

-   `ACCESS_KEY_ID` - DO Spaces/AWS S3 API Key ID
-   `SECRET_ACCESS_KEY` - DO Spaces/AWS S3 Secret access key
-   `GITHUB_EMAIL` - Email of GitHub user
-   `GITHUB_OAUTH_TOKEN` - GitHub auth token
-   `ETH_PRIVATE_KEY` - Ethereum private key for tests (without `0x` prefix)
-   `MANAGER_BRANCH` - Branch of the `skale-manager` to pull from DockerHub (`$MANAGER_BRANCH-latest` tag will be used)

### License

![GitHub](https://img.shields.io/github/license/skalenetwork/validator-cli.svg)

All contributions are made under the [GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html). See [LICENSE](LICENSE).
