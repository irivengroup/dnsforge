#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
legacy_name="lib-"validate".sh"




then
    echo "legacy validation library must not exist" >&2
    exit 1
fi

if grep -Rni "${legacy_name}" "${PROJECT_ROOT}/src" "${PROJECT_ROOT}/tests" >/dev/null 2>&1
then
    echo "legacy validation library references remain" >&2
    exit 1
fi



echo "Validation library consolidation OK"
