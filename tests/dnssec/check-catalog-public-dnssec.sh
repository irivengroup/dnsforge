#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

"${PROJECT_ROOT}/src/tools/generate-zone-catalog.sh"

external_master="${PROJECT_ROOT}/src/build/dns-proxy/zones/generated/external/master/split-example.invalid.conf"

test -f "${external_master}"
grep -q 'dnssec-policy "{{ DNSSEC_POLICY_NAME }}"' "${external_master}"
grep -q 'inline-signing yes' "${external_master}"

echo "Catalog public DNSSEC policy validation OK"
