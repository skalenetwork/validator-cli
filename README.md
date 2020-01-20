# SKALE Validator CLI

[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

## Table of Contents

1. [Installation](#installation)
2. [CLI usage](#cli-usage)  
    2.1 [Init](#init)  
    2.1 [Register](#register)  
3. [Development](#development)  

## Installation

- Download executable

```bash
VERSION_NUM=0.0.0 && sudo -E bash -c "curl -L https://skale-cli.sfo2.cdn.digitaloceanspaces.com/skale-$VERSION_NUM-`uname -s`-`uname -m` >  /usr/local/bin/skale"
```

- Apply executable permissions to the binary:

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

- `--endpoint/-e` - RPC endpoint of the node in the network where SKALE manager is deployed (`ws` or `wss`)
- `--contracts-url/-c` - - URL to SKALE Manager contracts ABI and addresses

Usage example:

```bash
sk-val init -e ws://geth.test.com:8546 -c https://test.com/manager.json
```

### Register

Register as a new SKALE validator

```bash
sk-val register
```

Required arguments:

- `--name/-n` - Validator name
- `--description/-d` - Validator description
- `--commission-rate/-c` - Commission rate (percentage)
- `--min-delegation` - Validator minimum delegation amount
- `--private-key/-p` - Validator's private key

Optional arguments:

- `--yes` - Confirmation flag

Usage example:

```bash
sk-val register -n test -d "test description" -c 20 --min-delegation 1000 -p 0x000000000...
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

- `ACCESS_KEY_ID` - DO Spaces/AWS S3 API Key ID
- `SECRET_ACCESS_KEY` - DO Spaces/AWS S3 Secret access key
- `GITHUB_EMAIL` - Email of GitHub user
- `GITHUB_OAUTH_TOKEN` - GitHub auth token
