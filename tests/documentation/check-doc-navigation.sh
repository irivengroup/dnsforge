#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DOCS_DIR="${PROJECT_ROOT}/docs"

check_file_exists() {
    local source_file="$1"
    local link_target="$2"
    local base_dir
    local target_path

    [[ "${link_target}" =~ ^https?:// ]] && return 0
    [[ "${link_target}" =~ ^# ]] && return 0

    link_target="${link_target%%#*}"
    [[ -z "${link_target}" ]] && return 0

    base_dir="$(dirname "${source_file}")"
    target_path="$(realpath -m "${base_dir}/${link_target}")"

    if [[ ! -e "${target_path}" ]]; then
        echo "Broken link in ${source_file}: ${link_target}" >&2
        exit 1
    fi
}

for doc in "${DOCS_DIR}"/*.md; do
    [[ "$(basename "${doc}")" == "index.md" ]] && continue
    head -n 5 "${doc}" | grep -q './index.md'
    tail -n 5 "${doc}" | grep -q './index.md'
done

for doc in "${DOCS_DIR}"/RUNBOOKS/*.md; do
    head -n 5 "${doc}" | grep -q '../index.md'
    tail -n 5 "${doc}" | grep -q '../index.md'
done

while IFS= read -r doc; do
    while IFS= read -r link; do
        target="$(printf '%s\n' "${link}" | sed -E 's/.*\]\(([^)]+)\).*/\1/')"
        check_file_exists "${doc}" "${target}"
    done < <(grep -oE '\[[^]]+\]\([^)]+\)' "${doc}" || true)
done < <(find "${DOCS_DIR}" -type f -name '*.md' | sort)

echo "Documentation navigation and link targets OK"
