#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

CONFIG_ROOT="${1:-/etc}"

if [[ -f "${CONFIG_ROOT}/named/conf.d/45-statistics.conf" ]]
then
    grep -q 'statistics-channels' "${CONFIG_ROOT}/named/conf.d/45-statistics.conf"
    grep -q '8053' "${CONFIG_ROOT}/named/conf.d/45-statistics.conf"
    echo "Statistics channel configuration found"
    exit 0
fi

echo "Statistics channel configuration not found under ${CONFIG_ROOT}" >&2
exit 1
