#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RENDER_ROOT="${PROJECT_ROOT}/src/render/dns-proxy/multivip"
grep -Rni 'primaries' "${RENDER_ROOT}/etc/named" >/dev/null
grep -Rni '192.0.2.10' "${RENDER_ROOT}/etc/named" >/dev/null
grep -Rni '192.0.2.20' "${RENDER_ROOT}/etc/named" >/dev/null
echo "Multi-VIP primaries validation OK"
