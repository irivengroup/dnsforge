#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

for inventory in "${PROJECT_ROOT}"/src/settings/dns-proxy/*.env
do
    grep -q '^ENABLE_PROXY_HA="no"' "${inventory}" || {
        echo "Proxy HA must be disabled by default in ${inventory}" >&2
        exit 1
    }
done

echo "Proxy HA optional default validation OK"
