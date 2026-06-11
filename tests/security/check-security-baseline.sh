#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

grep -Rni 'allow-transfer' "${PROJECT_ROOT}/src/dnsforge/infrastructure/templates" >/dev/null
grep -Rni 'allow-recursion' "${PROJECT_ROOT}/src/dnsforge/infrastructure/templates" >/dev/null
grep -Rni 'allow-query-cache' "${PROJECT_ROOT}/src/dnsforge/infrastructure/templates" >/dev/null
grep -Rni 'rate-limit' "${PROJECT_ROOT}/src/dnsforge/infrastructure/templates" >/dev/null
grep -Rni 'minimal-responses' "${PROJECT_ROOT}/src/dnsforge/infrastructure/templates" >/dev/null
grep -Rni 'dnssec-validation' "${PROJECT_ROOT}/src/dnsforge/infrastructure/templates" >/dev/null
grep -Rni 'response-policy' "${PROJECT_ROOT}/src/dnsforge/infrastructure/templates" >/dev/null

if test -d "${PROJECT_ROOT}/src/settings" && grep -RniE 'TSIG_SECRET="CHANGE_ME|RNDC_SECRET="CHANGE_ME' "${PROJECT_ROOT}/src/settings"
then
    echo "Default secret placeholders found in inventories. Replace before production." >&2
    exit 1
fi

echo "Security baseline source validation OK"
