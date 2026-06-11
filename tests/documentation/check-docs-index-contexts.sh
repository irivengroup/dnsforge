#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INDEX="${PROJECT_ROOT}/docs/index.md"

for section in \
    '## Présentation' \
    '## Déploiement' \
    '## Exploitation' \
    '## Sécurité' \
    '## Référence'
do
    grep -q "${section}" "${INDEX}" || {
        echo "Missing documentation context section: ${section}" >&2
        exit 1
    }
done

grep -q './ARCHITECTURE.md' "${INDEX}"
grep -q './DEPLOYMENT.md' "${INDEX}"
grep -q './OPERATIONS.md' "${INDEX}"
grep -q './SECURITY.md' "${INDEX}"
grep -q './TROUBLESHOOTING.md' "${INDEX}"

echo "Documentation index context validation OK"
