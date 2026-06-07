#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

fixture="${PROJECT_ROOT}/tests/fixtures/settings/dns-proxy/multivip.env"
target="${PROJECT_ROOT}/src/settings/dns-proxy/multivip.env"

cp "${fixture}" "${target}"
cat >> "${target}" <<'EOF'
ENABLE_PROXY_HA="yes"
PROXY_VIP_FRONT_IP="192.0.2.250/24"
PROXY_KEEPALIVED_INTERFACE="eth0"
PROXY_KEEPALIVED_STATE="MASTER"
PROXY_KEEPALIVED_PRIORITY="110"
PROXY_KEEPALIVED_VRID="61"
PROXY_KEEPALIVED_AUTH_PASS="testpass"
PROXY_HA_HEALTHCHECK_ZONE="split-example.invalid"
EOF

cleanup() {
    rm -f "${target}"
}
trap cleanup EXIT

"${PROJECT_ROOT}/src/tools/generate-zone-catalog.sh"
"${PROJECT_ROOT}/src/dnsProxyDeploy.sh" multivip --render-only

RENDER_ROOT="${PROJECT_ROOT}/src/render/dns-proxy/multivip"

test -x "${RENDER_ROOT}/opt/binddns/proxy-ha/check-proxy-ha.sh"
test -f "${RENDER_ROOT}/etc/keepalived/keepalived-proxy.conf"

grep -q '192.0.2.250/24' "${RENDER_ROOT}/etc/keepalived/keepalived-proxy.conf"
grep -q 'chk_binddns_proxy' "${RENDER_ROOT}/etc/keepalived/keepalived-proxy.conf"
grep -q 'split-example.invalid' "${RENDER_ROOT}/opt/binddns/proxy-ha/check-proxy-ha.sh"

bash "${PROJECT_ROOT}/tests/render/check-render-no-placeholders.sh" "${RENDER_ROOT}"

echo "Optional proxy HA render validation OK"
