#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

"${PROJECT_ROOT}/src/tools/generate-zone-catalog.sh"

test -f "${PROJECT_ROOT}/src/build/dns-proxy/zones/generated/external/master/split-example.invalid.conf"
test -f "${PROJECT_ROOT}/src/build/dns-proxy/zones/generated/internal/master/split-example.invalid.conf"
test -f "${PROJECT_ROOT}/src/build/dns-proxy/zones/generated/partner/master/split-example.invalid.conf"
test -f "${PROJECT_ROOT}/src/build/dns-proxy/zones/generated/external/secondary/catalog-secondary-a.invalid.conf"
test -f "${PROJECT_ROOT}/src/build/dns-proxy/zones/generated/internal/forward/catalog-forward-b.invalid.conf"
test -f "${PROJECT_ROOT}/src/build/dns-proxy/zones/generated/partner/forward/catalog-forward-b.invalid.conf"

grep -Rni 'split-example.invalid' "${PROJECT_ROOT}/src/build/dns-proxy/zones/generated" >/dev/null
grep -Rni 'AUTH_CLUSTER_A_PRIMARIES_BIND' "${PROJECT_ROOT}/src/build/dns-proxy/zones/generated" >/dev/null
grep -Rni 'AUTH_CLUSTER_B_BIND_LIST' "${PROJECT_ROOT}/src/build/dns-proxy/zones/generated" >/dev/null

echo "Zone catalog generation validation OK"
