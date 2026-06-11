#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
errors=0

while IFS= read -r file
do
    dir="$(dirname "${file}")"

    while IFS= read -r raw
    do
        link="$(printf '%s' "${raw}" | sed -E 's/.*\]\(([^)]+)\).*/\1/')"

        [[ -z "${link}" ]] && continue
        [[ "${link}" =~ ^https?:// ]] && continue
        [[ "${link}" =~ ^mailto: ]] && continue
        [[ "${link}" =~ ^# ]] && continue

        link="${link%%#*}"
        [[ -z "${link}" ]] && continue

        if [[ ! -e "${dir}/${link}" ]]
        then
            echo "Broken local link: ${file#${PROJECT_ROOT}/} -> ${link}" >&2
            errors=$((errors + 1))
        fi

    done < <(grep -oE '\[[^]]+\]\([^)]+\)' "${file}" || true)

done < <(find "${PROJECT_ROOT}" -name '*.md' -type f | sort)

if [[ "${errors}" -ne 0 ]]
then
    exit 1
fi

echo "Documentation local Markdown links validation OK"
