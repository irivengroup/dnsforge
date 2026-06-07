#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RENDER_ROOT="${1:-${PROJECT_ROOT}/src/render}"

if [[ ! -d "${RENDER_ROOT}" ]]
then
    echo "Render directory not found: ${RENDER_ROOT}" >&2
    exit 1
fi

if grep -RInE '\{\{[[:space:]]*[A-Z0-9_]+[[:space:]]*\}\}|CHANGE_ME|REPLACE_' "${RENDER_ROOT}"
then
    echo "Unresolved placeholder detected in rendered configuration" >&2
    exit 1
fi

echo "Rendered placeholder validation OK"
