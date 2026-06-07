#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

find "${PROJECT_ROOT}/src/build" -path '*/zones/*' -type f -name '*.conf' -print | while read -r zone_conf
do
    grep -q '^zone "' "${zone_conf}" || {
        echo "Zone declaration missing in ${zone_conf}" >&2
        exit 1
    }

    grep -q '};' "${zone_conf}" || {
        echo "Zone declaration does not appear closed in ${zone_conf}" >&2
        exit 1
    }
done

echo "Zone source validation OK"
