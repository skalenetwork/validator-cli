#!/usr/bin/env bash
#
# Darwin ARM binary build, intended to run inside `nix develop`.
#
# The Nix dev shell provides swig and openssl (with LDFLAGS, CFLAGS, and
# SWIG_FEATURES pre-exported), so `uv sync` can compile m2crypto without
# any separate brew or nix-store invocations.
#
# Usage (from repo root):
#   nix develop --command bash scripts/build_darwin_nix.sh VERSION BRANCH

set -e

VERSION="$1"
BRANCH="$2"

if [ -z "$VERSION" ] || [ -z "$BRANCH" ]; then
    echo "Usage: build_darwin_nix.sh VERSION BRANCH" >&2
    exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

## Install Python deps (reads uv.lock; m2crypto compiled with Nix's swig+openssl)
uv sync --prerelease allow --extra dev

## Build PyInstaller binary
uv run "$DIR/build.sh" "$VERSION" "$BRANCH"
