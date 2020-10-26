# SKALE Validator CLI

![Build and publish](https://github.com/skalenetwork/validator-cli/workflows/Build%20and%20publish/badge.svg)
![Test](https://github.com/skalenetwork/validator-cli/workflows/Test/badge.svg)
[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

## Table of Contents

1.  [Installation](#installation)
2.  [CLI usage](#cli-usage)  
    2.1 [Init](#init)  
    2.2 [Validator commands](#validator-commands)  
    2.3 [Holder commands](#holder-commands)  
    2.4 [Metrics commands](#metrics-commands)  
    2.5 [Wallet commands](#wallet-commands)
3.  [Development](#development)  

## Installation

### Requirements

-   Linux x86_64 machine

-   Download executable

```bash
VERSION_NUM={put the version number here} && sudo -E bash -c "curl -L https://github.com/skalenetwork/validator-cli/releases/download/$VERSION_NUM/sk-val-$VERSION_NUM-`uname -s`-`uname -m` >  /usr/local/bin/sk-val"
```

-   Apply executable permissions to the binary:

```bash
sudo chmod +x /usr/local/bin/sk-val
```

### Where to find out the latest version?

All validator-cli version numbers are available here: https://github.com/skalenetwork/validator-cli/releases

## CLI Usage

### Init

Download SKALE Manager contracts info and set the endpoint.

```bash
sk-val init
```

Required arguments:

-   `--endpoint/-e` - RPC endpoint of the node in the network where SKALE manager is deployed (`ws` or `wss`)
-   `--contracts-url/-c` - - URL to SKALE Manager contracts ABI and addresses
-   `-w/--wallet` - Type of the wallet that will be used for signing transactions (software, sgx or hardware)

If you want to use sgx wallet you need to initialize it first (see **SGX commands**)

Usage example:

```bash
sk-val init -e ws://geth.test.com:8546 -c https://test.com/manager.json --wallet software
```

### SGX commands

#### Init 
 Initialize sgx wallet  
 ```bash
sk-val sgx init [SGX_SERVER_URL]
```
Optional arguments:
-   `--force/-f` - Rewrite current sgx wallet data
-  `--ssl-port` - Port that is used by sgx server to establish tls connection

#### Info
Print sgx wallet information
```bash
sk-val sgx info 
```
Optional arguments:
-   `--raw` - Print info in plain json

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
sk-val validator register -n test -d "test description" -c 20 --min-delegation 1000 --pk-file ./pk.txt
```

#### List

List of available validators

```bash
sk-val validator ls
```

Options:

-   `--wei/-w` - Show tokens amount in wei

#### Delegations

List of delegations for validator ID

```bash
sk-val validator delegations [VALIDATOR_ID]
```

Required params:

1) VALIDATOR_ID - ID of the validator

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

#### Accept all pending delegations

Accept ALL pending delegations request for the address.  
List with all pending delegations to be accepted will be shown. After this user should confirm the operation.

```bash
sk-val validator accept-all-delegations --pk-file ./pk.txt
```

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)

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
sk-val validator link-address [ADDRESS] [NODE_SIGNATURE] --pk-file ./pk.txt
```

Required params:

1) Address - Ethereum address that will be linked
2) Node signature - Signature of the node that you can get using `skale node signature`
   command from skale-node-cli

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
4) Fee rate (percent - %)
5) Minimum delegation amount (SKL)
6) Accepting new delegation requests

#### Withdraw fee

Withdraw earned fee to specified address

```bash
sk-val validator withdraw-fee [RECIPIENT_ADDRESS] --pk-file ./pk.txt
```

Required params:

1) RECIPIENT_ADDRESS - Address to transfer bounty

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)
-   `--yes` - Confirmation flag

#### Set MDA

Set a new minimum delegation amount for the validator

```bash
sk-val validator set-mda [NEW_MDA] --pk-file ./pk.txt
```

Required params:

1) NEW_MDA - New MDA value

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)
-   `--yes` - Confirmation flag

#### Request address change

Request address change for the validator

```bash
sk-val validator change-address [ADDRESS] --pk-file ./pk.txt
```

Required params:

1) ADDRESS - New validator address

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)
-   `--yes` - Confirmation flag

#### Confirm address change

Confirm address change for the validator. Should be executed using new validator key.

```bash
sk-val validator confirm-address [VALIDATOR_ID] --pk-file ./pk.txt
```

Required params:

1) VALIDATOR_ID - ID of the validator

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)
-   `--yes` - Confirmation flag

#### Earned fees

Get earned fee amount for the validator address

```bash
sk-val validator earned-fees [ADDRESS]
```

Required params:

1) ADDRESS - Validator address

Optional arguments:

-   `--wei` - Show amount in wei

### Holder commands

#### Delegate

Delegate tokens to validator

```bash
sk-val holder delegate
```

Required arguments:

-   `--validator-id` - ID of the validator to delegate
-   `--amount` - Amount of SKALE tokens to delegate
-   `--delegation-period` - Delegation period (in months - only `2` avaliable now)
-   `--info` - Delegation request info

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)

#### Delegations

List of delegations for address

```bash
sk-val holder delegations [ADDRESS]
```

Required arguments:

1) ADDRESS - Ethereum address of the token holder

Options:

-   `--wei/-w` - Show tokens amount in wei

#### Cancel pending delegation

Cancel pending delegation request

```bash
sk-val holder cancel-delegation [DELEGATION_ID]
```

Required params:

1) Delegation ID - ID of the delegation to cancel

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)

#### Request undelegation

Request undelegation in the end of delegation period

```bash
sk-val holder undelegate [DELEGATION_ID]
```

Required params:

1) Delegation ID - ID of the delegation

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)

#### Withdraw bounty

Withdraw earned bounty to specified address

```bash
sk-val holder withdraw-bounty [VALIDATOR_ID] [RECIPIENT_ADDRESS] --pk-file ./pk.txt
```

Required params:

1) VALIDATOR_ID - ID of the validator
2) RECIPIENT_ADDRESS - Address to transfer bounty

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)
-   `--yes` - Confirmation flag

#### Locked

Show amount of locked tokens for address

```bash
sk-val holder locked [ADDRESS]
```

Required arguments:

1) ADDRESS - Ethereum address of the token holder

Options:

-   `--wei/-w` - Show tokens amount in wei

#### Earned bounties

Get earned bounties amount by token holder for the validator ID

```bash
sk-val holder earned-bounties [VALIDATOR_ID] [ADDRESS]
```

Required params:

1) VALIDATOR_ID - ID of the validator
1) ADDRESS - Token holder address

Optional arguments:

-   `--wei` - Show amount in wei

### Metrics commands

#### Node metrics

Shows a list of metrics and bounties for a given node ID

```bash
sk-val metrics node
```

Required arguments:

-   `--index/-id` - Node ID

Collecting metrics from the SKALE Manager may take a long time. It is therefore recommended to use optional arguments to limit output by filtering by time period or limiting the number of records to show.

Optional arguments:

-   `--since/-s` - Show requested data since a given date inclusively (e.g. 2020-01-20)
-   `--till/-t` - Show requested data before a given date not inclusively (e.g. 2020-01-21)
-   `--wei/-w` - Show bounty amount in wei
-   `--to-file/-f` - Export metrics to .csv file (with a given file pathname)

Usage example:

```bash
sk-val metrics node -id 1 --since 2020-04-30 --till 2020-05-01 -w -f /home/user/filename.csv
```

#### Validator metrics

Shows a list of metrics and bounties for all nodes for a given validator ID

```bash
sk-val metrics validator
```

Required arguments:

-   `--index/-id` - Validator ID

Collecting metrics from the SKALE Manager may take a long time. It is therefore recommended to use optional arguments to limit output by filtering by time period or limiting the number of records to show.

Optional arguments:

-   `--since/-s` - Show requested data since a given date inclusively (e.g. 2020-01-20)
-   `--till/-t` - Show requested data before a given date not inclusively (e.g. 2020-01-21)
-   `--wei/-w` - Show bounty amount in wei
-   `--to-file/-f` - Export metrics to .csv file (with a given file pathname)

Usage example:

```bash
sk-val metrics validator -id 1 --since 2020-04-30 --till 2020-05-01 -w -f /home/user/filename.csv
```

### Wallet commands

#### Setup Ledger

This command works only if you're using the Ledger wallet

```bash
sk-val wallet setup-ledger
```

Required params:

-   `--address-index` - Index of the address to use (starting from `0`)
-   `--keys-type` - Type of the Ledger keys (live or legacy)

#### Send ETH tokens

Send ETH tokens to specific address

```bash
sk-val wallet send-eth [ADDRESS] [AMOUNT]
```

Required arguments:

1) ADDRESS - Ethereum receiver address
2) AMOUNT - Amount of ETH tokens to send

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)
-   `--yes` - Confirmation flag

Usage example:

```bash
sk-val wallet send-eth 0x01C19c5d3Ad1C3014145fC82263Fbae09e23924A 0.01 --pk-file ./pk.txt --yes
```

#### Send SKL tokens

Send SKL tokens to specific address

```bash
sk-val wallet send-skl [ADDRESS] [AMOUNT]
```

Required arguments:

1) ADDRESS - Ethereum receiver address
2) AMOUNT - Amount of SKL tokens to send

Optional arguments:

-   `--pk-file` - Path to file with private key (only for `software` wallet type)
-   `--yes` - Confirmation flag

Usage example:

```bash
sk-val wallet send-skl 0x01C19c5d3Ad1C3014145fC82263Fbae09e23924A 0.01 --pk-file ./pk.txt --yes
```

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
