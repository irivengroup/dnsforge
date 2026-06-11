#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
README="${PROJECT_ROOT}/README.md"

grep -q '^# ZoneForge DNSaaS' "${README}"
grep -q 'Plateforme de Déploiement et de Configuration DNS as a Service' "${README}"
grep -q 'docs/images/zoneforge-dnsaas-architecture.png' "${README}"
grep -q './docs/index.md' "${README}"
grep -q '© IRIVEN Group — All Rights Reserved' "${README}"

for forbidden in \
    'journalctl -u' \
    'systemctl restart' \
    'named-checkconf -z' \
    'rndc reload' \
    'restorecon -Rv'
do
    if grep -q "${forbidden}" "${README}"
    then
        echo "README contains operational runbook detail: ${forbidden}" >&2
        exit 1
    fi
done

echo "README product scope validation OK"
