#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "${PROJECT_ROOT}/src/libs/lib-logging.sh"
source "${PROJECT_ROOT}/src/libs/lib-network.sh"

expected=$'10.0.0.1\n10.0.0.2\n10.0.0.3\n10.0.0.4'
actual="$(normalize_list '10.0.0.1 ; 10.0.0.2,10.0.0.3 10.0.0.4')"
[[ "${actual}" == "${expected}" ]] || { echo "normalize_list failed" >&2; exit 1; }

validate_ip_list '10.0.0.1 ; 10.0.0.2,10.0.0.3 10.0.0.4'

grep -q '10.0.0.1;' <<< "$(build_bind_ip_list '10.0.0.1 ; 10.0.0.2')"
grep -q '10.0.0.2;' <<< "$(build_bind_ip_list '10.0.0.1 ; 10.0.0.2')"
grep -q '10.0.0.1 key "xfr-key";' <<< "$(build_bind_tsig_list '10.0.0.1, 10.0.0.2' 'xfr-key')"

echo "Universal list normalization validation OK"
