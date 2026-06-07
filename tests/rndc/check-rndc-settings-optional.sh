#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if grep -RniE '^RNDC_(KEY_NAME|SECRET)=' "${PROJECT_ROOT}/src/settings" >/dev/null
then
    echo "RNDC_KEY_NAME and RNDC_SECRET must not be mandatory in src/settings" >&2
    exit 1
fi
echo "RNDC settings optional validation OK"
