#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if ! command -v named-checkconf >/dev/null 2>&1
then
    echo "named-checkconf unavailable - skipping rendered BIND validation"
    exit 0
fi

found=0

while IFS= read -r named_conf
do
    found=1
    echo "Checking ${named_conf}"
    named-checkconf -z "${named_conf}"
done < <(find "${PROJECT_ROOT}/src/render" -type f -name named.conf | sort)

if [[ "${found}" -eq 0 ]]
then
    echo "No rendered named.conf found. Run --render-only before this test." >&2
    exit 1
fi

echo "Rendered BIND config validation OK"
