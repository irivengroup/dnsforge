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

if [[ ! -d "${RENDER_ROOT}" ]]
then
    echo "Render root not found: ${RENDER_ROOT}" >&2
    exit 1
fi

diff_path() {
    local rendered="$1"
    local live="$2"

    if [[ -e "${rendered}" && -e "${live}" ]]
    then
        diff -ruN "${live}" "${rendered}" || true
    elif [[ -e "${rendered}" ]]
    then
        echo "NEW ${live} <= ${rendered}"
    fi
}

diff_path "${RENDER_ROOT}/etc/named.conf" "/etc/named.conf"
diff_path "${RENDER_ROOT}/etc/named" "/etc/named"
diff_path "${RENDER_ROOT}/var/named" "/var/named"

if [[ -e "${RENDER_ROOT}/etc/keepalived" ]]
then
    diff_path "${RENDER_ROOT}/etc/keepalived" "/etc/keepalived"
fi
