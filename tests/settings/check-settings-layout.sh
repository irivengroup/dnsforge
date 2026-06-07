#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

test -d "${PROJECT_ROOT}/src/settings/dns-proxy"
test -d "${PROJECT_ROOT}/src/settings/dns-authoritative"

if [[ -d "${PROJECT_ROOT}/src/inventories" ]]
then
    echo "Legacy src/inventories directory must not exist" >&2
    exit 1
fi

find "${PROJECT_ROOT}/src/settings" -type f -name '*.env' -print | grep -q .

echo "Settings layout validation OK"
