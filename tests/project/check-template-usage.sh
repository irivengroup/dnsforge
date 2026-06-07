#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

unused=0

while IFS= read -r template_file
do
    rel_path="${template_file#${PROJECT_ROOT}/}"
    base_name="$(basename "${template_file}")"

    case "${base_name}" in
        *.tpl)
            # Reusable templates are allowed even if not rendered directly.
            continue
            ;;
    esac

    if ! grep -R --fixed-strings "${rel_path}" "${PROJECT_ROOT}/src" "${PROJECT_ROOT}/tests" >/dev/null 2>&1
    then
        echo "Template appears unused: ${rel_path}" >&2
        unused=$((unused + 1))
    fi

done < <(find "${PROJECT_ROOT}/src/build" -type f \( -name '*.j2' -o -name '*.tpl' \) | sort)

if [[ "${unused}" -ne 0 ]]
then
    exit 1
fi

echo "Template usage validation OK"
