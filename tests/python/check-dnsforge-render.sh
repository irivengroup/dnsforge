#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP_SETTINGS="${PROJECT_ROOT}/src/settings/dns-proxy/render-test.env"

cat > "${TMP_SETTINGS}" <<'EOF'
ROLE="dns-proxy"
FRONT_IP="192.0.2.53"
BACK_IP="198.51.100.53"
ADM_IP="203.0.113.53"
ENABLE_RPZ="yes"
ENABLE_RRL="yes"
ENABLE_DNSSEC="yes"
EOF

trap 'rm -f "${TMP_SETTINGS}"; rm -rf "${PROJECT_ROOT}/src/render/dns-proxy/render-test"' EXIT

PYTHONPATH="${PROJECT_ROOT}/src" python3 -m dnsforge.interfaces.cli.main \
  --project-root "${PROJECT_ROOT}" render proxy render-test --type forwarder

test -f "${PROJECT_ROOT}/src/render/dns-proxy/render-test/etc/named.conf"
test ! -e "${PROJECT_ROOT}/src/render/dns-proxy/render-test/etc/named/45-local-zones.conf"
test ! -d "${PROJECT_ROOT}/src/render/dns-proxy/render-test/var/named/master"

PYTHONPATH="${PROJECT_ROOT}/src" python3 -m dnsforge.interfaces.cli.main \
  --project-root "${PROJECT_ROOT}" render proxy render-test --type hybrid

test -f "${PROJECT_ROOT}/src/render/dns-proxy/render-test/etc/named/45-local-zones.conf"
test -d "${PROJECT_ROOT}/src/render/dns-proxy/render-test/var/named/master"

echo "dnsforge render validation OK"
