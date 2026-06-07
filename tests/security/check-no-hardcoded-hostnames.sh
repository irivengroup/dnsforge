#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if grep -RniE '\b(srv[0-9]+|svr[0-9]+)[a-z]?\b' \
    "${PROJECT_ROOT}/src/build" \
    "${PROJECT_ROOT}/src/libs" \
    "${PROJECT_ROOT}/src/"*.sh 2>/dev/null
then
    echo "Hardcoded server-like hostname found in source code/templates." >&2
    exit 1
fi

echo "No hardcoded server-like hostnames found in source code/templates"
