#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if grep -RInE '\{[[:space:]]*[^}]+;[[:space:]]*\};' "${PROJECT_ROOT}/src/build" --include='*.j2' --include='*.tpl'
then
    echo "Inline BIND block detected. Please format blocks on multiple lines." >&2
    exit 1
fi

echo "BIND template formatting OK"
