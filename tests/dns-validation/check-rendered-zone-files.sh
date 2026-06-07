#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if ! command -v named-checkzone >/dev/null 2>&1
then
    echo "named-checkzone unavailable - skipping zone file validation"
    exit 0
fi

found=0

while IFS= read -r zone_file
do
    found=1

    zone_name="$(basename "${zone_file}")"
    zone_name="${zone_name%.zone}"
    zone_name="${zone_name%.db}"

    echo "Checking zone ${zone_name}: ${zone_file}"
    named-checkzone "${zone_name}" "${zone_file}" >/dev/null

done < <(find "${PROJECT_ROOT}/src/render" -path '*/var/named/*' -type f \( -name '*.zone' -o -name '*.db' \) | sort)

if [[ "${found}" -eq 0 ]]
then
    echo "No rendered zone files found. Run --render-only before this test."
fi

echo "Rendered zone file validation OK"
