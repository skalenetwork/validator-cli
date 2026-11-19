#!/usr/bin/env bash
set -e

VERSION=$1
BRANCH=$2

cd "$(dirname "${BASH_SOURCE[0]}")/.."

bash scripts/generate_info.sh "$VERSION" "$BRANCH"

EXECUTABLE_NAME=sk-val-$VERSION-$(uname -s)-$(uname -m)

pyinstaller main.spec

mv dist/main "dist/$EXECUTABLE_NAME"

echo "Built validator-cli v$VERSION, branch: $BRANCH"
echo "Executable: $EXECUTABLE_NAME"
