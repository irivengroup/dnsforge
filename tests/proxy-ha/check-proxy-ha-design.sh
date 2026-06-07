#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

proxy_inventory_count="$(find "${PROJECT_ROOT}/src/settings/dns-proxy" -maxdepth 1 -type f -name '*.env' | wc -l)"

if [[ "${proxy_inventory_count}" -lt 2 ]]
then
    echo "At least two dns-proxy inventories are expected for default DNS1/DNS2 HA mode." >&2
    exit 1
fi

for inventory in "${PROJECT_ROOT}"/src/settings/dns-proxy/*.env
do
    grep -q '^ENABLE_PROXY_HA="no"' "${inventory}" || {
        echo "Default proxy HA mode must remain disabled in ${inventory}" >&2
        exit 1
    }
done

echo "DNS Proxy default HA design validation OK: DNS1/DNS2 without VIP"
