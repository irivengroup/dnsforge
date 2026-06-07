#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

for required_dir in \
    "${PROJECT_ROOT}/src/build/dns-proxy/zones/external/master" \
    "${PROJECT_ROOT}/src/build/dns-proxy/zones/internal/master"
do
    [[ -d "${required_dir}" ]] || {
        echo "Missing proxy master directory: ${required_dir}" >&2
        exit 1
    }
done

find "${PROJECT_ROOT}/src/build/dns-proxy/zones" -type f -path '*/master/*.conf' -print | while read -r zone_conf
do
    grep -q 'type master;' "${zone_conf}" || {
        echo "Proxy master declaration missing 'type master;' in ${zone_conf}" >&2
        exit 1
    }

    grep -q 'allow-transfer' "${zone_conf}" || {
        echo "Proxy master declaration should explicitly define allow-transfer in ${zone_conf}" >&2
        exit 1
    }
done

echo "Proxy master zone validation OK"
