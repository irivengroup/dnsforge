#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

test -f "${PROJECT_ROOT}/src/build/common/dnssec/dnssec-policy.conf.j2"
test -f "${PROJECT_ROOT}/src/build/common/dnssec/dnssec-options.conf.j2"
test -f "${PROJECT_ROOT}/src/build/dns-authoritative/templates/master-zone-dnssec.conf.tpl"

grep -q 'dnssec-policy' "${PROJECT_ROOT}/src/build/common/dnssec/dnssec-policy.conf.j2"
grep -q 'key-directory' "${PROJECT_ROOT}/src/build/common/dnssec/dnssec-options.conf.j2"
grep -q 'inline-signing yes' "${PROJECT_ROOT}/src/build/dns-authoritative/templates/master-zone-dnssec.conf.tpl"

echo "DNSSEC template validation OK"
