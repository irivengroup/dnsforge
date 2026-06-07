#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

found=0

while IFS= read -r index_file
do
    found=1

    while IFS= read -r include_line
    do
        [[ -z "${include_line}" ]] && continue

        included_path="$(printf '%s\n' "${include_line}" | sed -E 's@include "([^"]+)";@\1@')"

        [[ "${included_path}" == "${include_line}" ]] && continue

        candidate="$(dirname "${index_file}")/$(basename "${included_path}")"

        if [[ ! -f "${candidate}" ]]
        then
            echo "Included zone file not found from ${index_file}: ${included_path}" >&2
            exit 1
        fi

    done < "${index_file}"

done < <(find "${PROJECT_ROOT}/src/render" -type f -name 'zones.index.conf' -print)

if [[ "${found}" -eq 0 ]]
then
    echo "No zones.index.conf found under src/render. Run a --render-only deployment first." >&2
    exit 1
fi

echo "Zone index validation OK"
