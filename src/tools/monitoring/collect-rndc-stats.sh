#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

STATS_DIR="${STATS_DIR:-/var/named/data}"
OUTPUT_DIR="${OUTPUT_DIR:-/var/log/named/stats}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

mkdir -p "${OUTPUT_DIR}"

if ! command -v rndc >/dev/null 2>&1
then
    echo "rndc not found" >&2
    exit 1
fi

rndc stats

if [[ -f "${STATS_DIR}/named_stats.txt" ]]
then
    cp "${STATS_DIR}/named_stats.txt" "${OUTPUT_DIR}/named_stats-${TIMESTAMP}.txt"
    echo "${OUTPUT_DIR}/named_stats-${TIMESTAMP}.txt"
else
    echo "named_stats.txt not found under ${STATS_DIR}" >&2
    exit 1
fi
