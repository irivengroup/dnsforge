#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RENDER_ROOT="${1:-${PROJECT_ROOT}/src/render}"

require_path() {
    local required_path="$1"

    if [[ ! -e "${required_path}" ]]
    then
        echo "Missing rendered path: ${required_path}" >&2
        exit 1
    fi
}

found=0

while IFS= read -r node_root
do
    found=1

    role="$(basename "$(dirname "${node_root}")")"
    node="$(basename "${node_root}")"

    echo "Checking rendered paths for ${role}/${node}"

    require_path "${node_root}/etc/named.conf"
    require_path "${node_root}/etc/named/conf.d"
    require_path "${node_root}/var/named"
    require_path "${node_root}/var/log/named"

    if [[ "${role}" == "dns-proxy" ]]
    then
        require_path "${node_root}/etc/named/views/external/master/zones.index.conf"
        require_path "${node_root}/etc/named/views/external/secondary/zones.index.conf"
        require_path "${node_root}/etc/named/views/external/forward/zones.index.conf"
        require_path "${node_root}/etc/named/views/internal/master/zones.index.conf"
        require_path "${node_root}/etc/named/views/internal/secondary/zones.index.conf"
        require_path "${node_root}/etc/named/views/internal/forward/zones.index.conf"
        require_path "${node_root}/etc/named/views/internal/reverse/zones.index.conf"
        require_path "${node_root}/etc/named/rpz/50-rpz.conf"
        require_path "${node_root}/etc/named/rpz/rpz-zone.conf"
        require_path "${node_root}/var/named/rpz"
    fi

    if [[ "${role}" == "dns-authoritative" ]]
    then
        require_path "${node_root}/etc/named/zones/external/master/zones.index.conf"
        require_path "${node_root}/etc/named/zones/internal/master/zones.index.conf"
        require_path "${node_root}/etc/named/zones/reverse/master/zones.index.conf"
        require_path "${node_root}/etc/keepalived/keepalived.conf"
        require_path "${node_root}/var/named/master/external"
        require_path "${node_root}/var/named/master/internal"
        require_path "${node_root}/var/named/master/reverse"
    fi

done < <(find "${RENDER_ROOT}" -mindepth 2 -maxdepth 2 -type d | sort)

if [[ "${found}" -eq 0 ]]
then
    echo "No rendered node found under ${RENDER_ROOT}. Run --render-only first." >&2
    exit 1
fi

echo "Rendered path validation OK"
