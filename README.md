# SKALE Validator CLI

![Build and publish](https://github.com/skalenetwork/validator-cli/workflows/Build%20and%20publish/badge.svg)
![Test](https://github.com/skalenetwork/validator-cli/workflows/Test/badge.svg)
[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

## Installation

### Requirements

-   Linux x86_64 machine

-   Download executable

```shell
VERSION_NUM={put the version number here} && sudo -E bash -c "curl -L https://github.com/skalenetwork/validator-cli/releases/download/$VERSION_NUM/sk-val-$VERSION_NUM-`uname -s`-`uname -m` >  /usr/local/bin/sk-val"
```

-   Apply executable permissions to the binary:

```shell
sudo chmod +x /usr/local/bin/sk-val
```

### Where to find out the latest version?

All validator-cli version numbers are available here: https://github.com/skalenetwork/validator-cli/releases

## Development

### Setup repo

#### Install development dependencies

```shell
pip install -e .[dev]
```

##### Add flake8 git hook

In file `.git/hooks/pre-commit` add:

```shell
#!/bin/sh
flake8 .
```

### Debugging

Run commands in dev mode:

```shell
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
