#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

bash -n "${PROJECT_ROOT}/src/build/dns-proxy/ha/check-proxy-ha.sh.j2"
grep -q 'vrrp_instance VI_BINDDNS_PROXY' "${PROJECT_ROOT}/src/build/dns-proxy/keepalived/keepalived-proxy.conf.j2"
grep -q 'track_script' "${PROJECT_ROOT}/src/build/dns-proxy/keepalived/keepalived-proxy.conf.j2"

echo "Optional proxy HA syntax validation OK"
