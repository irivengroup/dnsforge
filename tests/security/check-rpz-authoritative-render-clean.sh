#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if find "${PROJECT_ROOT}/src/build/dns-authoritative" -type f \( -name '*.j2' -o -name '*.tpl' -o -name '*.conf' \) -print0 2>/dev/null \
    | xargs -0 grep -RniE 'include .*rpz|response-policy' >/dev/null 2>&1
then
    echo "Authoritative templates must not include RPZ or response-policy" >&2
    exit 1
fi

echo "RPZ authoritative render clean validation OK"
