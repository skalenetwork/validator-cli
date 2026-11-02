#!/usr/bin/env bash
set -e

VERSION=$1
BRANCH=$2

if [ -z "$VERSION" ] || [ -z "$BRANCH" ]; then
    echo 'Usage: generate_info.sh VERSION BRANCH' >&2
    exit 1
fi

cat > "$(dirname "${BASH_SOURCE[0]}")/../cli/info.py" <<EOF
BUILD_DATETIME = '$(date '+%Y-%m-%d %H:%M:%S')'
COMMIT = '$(git rev-parse HEAD)'
BRANCH = '$BRANCH'
OS = '$(uname -s)-$(uname -m)'
VERSION = '$VERSION'
EOF
