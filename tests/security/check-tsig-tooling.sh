#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

test -x "${PROJECT_ROOT}/src/tools/generate-tsig.sh"
test -x "${PROJECT_ROOT}/src/tools/check-secrets.sh"

grep -Rni 'TSIG_SECRET' "${PROJECT_ROOT}/src/settings" >/dev/null
grep -Rni 'TSIG_KEY_NAME' "${PROJECT_ROOT}/src/settings" >/dev/null

echo "TSIG tooling validation OK"
