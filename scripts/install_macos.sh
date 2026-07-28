#!/usr/bin/env bash
#
# Darwin ARM (Apple Silicon) install script for validator-cli.
#
# Installs sk-val into the uv tool environment. Several transitive
# dependencies (m2crypto, pyzmq, pandas, pyyaml, cytoolz) require either
# version overrides or build-time environment to compile on Python 3.13+ /
# macOS ARM. This script handles all of that automatically.
#
# Prerequisites:
#   - uv (https://docs.astral.sh/uv/)
#   - Nix (https://nixos.org/) — provides swig for m2crypto
#   - brew + openssl@3 — provides OpenSSL headers for m2crypto

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(dirname "$DIR")"

## Prerequisites check

command -v uv  >/dev/null 2>&1 || { echo "uv is not installed — see https://docs.astral.sh/uv/"; exit 1; }
command -v nix >/dev/null 2>&1 || { echo "nix is not installed — see https://nixos.org/download/"; exit 1; }
command -v brew >/dev/null 2>&1 || { echo "brew is not installed — see https://brew.sh/"; exit 1; }

OPENSSL_PREFIX="$(HOMEBREW_NO_AUTO_UPDATE=1 brew --prefix openssl 2>/dev/null | tail -1)"
if [ -z "$OPENSSL_PREFIX" ] || [ ! -d "$OPENSSL_PREFIX" ]; then
    echo "OpenSSL not found via brew. Install with: brew install openssl"
    exit 1
fi

## Ensure swig is available via nix

SWIG_PATH="$(nix build nixpkgs#swig --no-link --print-out-paths 2>/dev/null)/bin"
if [ ! -x "${SWIG_PATH}/swig" ]; then
    echo "Failed to locate swig in nix store."
    exit 1
fi

## Install

export PATH="${SWIG_PATH}:${PATH}"
export LDFLAGS="-L${OPENSSL_PREFIX}/lib"
export CFLAGS="-I${OPENSSL_PREFIX}/include"
export SWIG_FEATURES="-cpperraswarn -includeall -I${OPENSSL_PREFIX}/include"

uv tool install \
    --prerelease allow \
    --overrides "${REPO_ROOT}/darwin-overrides.txt" \
    "$@" \
    "${REPO_ROOT}"
