#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

test -f "${PROJECT_ROOT}/src/build/common/dnssec/dnssec-policy-enterprise.conf.j2"
test -f "${PROJECT_ROOT}/src/build/dns-authoritative/templates/master-zone-dnssec-enterprise.conf.tpl"

grep -q 'ksk lifetime' "${PROJECT_ROOT}/src/build/common/dnssec/dnssec-policy-enterprise.conf.j2"
grep -q 'zsk lifetime' "${PROJECT_ROOT}/src/build/common/dnssec/dnssec-policy-enterprise.conf.j2"
grep -q 'nsec3param' "${PROJECT_ROOT}/src/build/common/dnssec/dnssec-policy-enterprise.conf.j2"
grep -q 'cds-digest-types' "${PROJECT_ROOT}/src/build/common/dnssec/dnssec-policy-enterprise.conf.j2"
grep -q 'inline-signing yes' "${PROJECT_ROOT}/src/build/dns-authoritative/templates/master-zone-dnssec-enterprise.conf.tpl"

echo "DNSSEC enterprise template validation OK"
