#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

found=0

while IFS= read -r node_root
do
    found=1
    test -f "${node_root}/etc/named/dnssec/dnssec-policy.conf"
    test -f "${node_root}/etc/named/dnssec/dnssec-options.conf"
    test -d "${node_root}/var/named/dnssec"
done < <(find "${PROJECT_ROOT}/src/render" -mindepth 2 -maxdepth 2 -type d | sort)

if [[ "${found}" -eq 0 ]]
then
    echo "No rendered node found. Run --render-only first." >&2
    exit 1
fi

echo "DNSSEC render validation OK"
