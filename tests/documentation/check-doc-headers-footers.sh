#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

while IFS= read -r file
do
    head -n 5 "${file}" | grep -q 'ZoneForge DNSaaS' || {
        echo "Missing ZoneForge header: ${file#${PROJECT_ROOT}/}" >&2
        exit 1
    }

    grep -q '© IRIVEN Group — All Rights Reserved' "${file}" || {
        echo "Missing IRIVEN copyright footer: ${file#${PROJECT_ROOT}/}" >&2
        exit 1
    }

done < <(find "${PROJECT_ROOT}/docs" -name '*.md' -type f | sort)

echo "Documentation headers and footers validation OK"
