#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if grep -RniE 'TSIG_SECRET="CHANGE_ME|RNDC_SECRET="CHANGE_ME|REPLACE_' "${PROJECT_ROOT}/src/settings"
then
    echo "Secret or inventory placeholders found. Replace them before production." >&2
    exit 1
fi

echo "Inventory secret check OK"
