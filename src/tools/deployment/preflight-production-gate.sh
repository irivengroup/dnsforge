#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

RENDER_ROOT="${1:-}"

if [[ -z "${RENDER_ROOT}" ]]
then
    echo "Usage: $0 <render-root>" >&2
    exit 1
fi

test -d "${RENDER_ROOT}"
test -f "${RENDER_ROOT}/etc/named.conf"

if grep -RInE '\{\{[[:space:]]*[A-Z0-9_]+[[:space:]]*\}\}|CHANGE_ME|REPLACE_' "${RENDER_ROOT}"
then
    echo "Unresolved placeholders found in render root" >&2
    exit 1
fi

if command -v named-checkconf >/dev/null 2>&1
then
    named-checkconf -z "${RENDER_ROOT}/etc/named.conf"
else
    echo "WARNING named-checkconf unavailable; install bind-utils for full gate" >&2
fi

find "${RENDER_ROOT}/etc/named" -type f -name '*.conf' -print | sort

echo "Production preflight gate OK"
