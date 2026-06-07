#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

bash "${PROJECT_ROOT}/tests/integration/render-proxy-multivip.sh"
RENDER_ROOT="${PROJECT_ROOT}/src/render/dns-proxy/multivip"

test -f "${RENDER_ROOT}/etc/named/conf.d/00-acl.conf"
test -f "${RENDER_ROOT}/etc/named/conf.d/60-views.conf"
test -f "${RENDER_ROOT}/etc/named/views/partner/secondary/example-partner.conf"

grep -Rni 'partner_clients' "${RENDER_ROOT}/etc/named/conf.d/00-acl.conf" >/dev/null
grep -Rni 'view "partner"' "${RENDER_ROOT}/etc/named/conf.d/60-views.conf" >/dev/null
grep -Rni 'partner-zone.invalid' "${RENDER_ROOT}/etc/named/views/partner/secondary/example-partner.conf" >/dev/null
grep -Rni 'allow-query' "${RENDER_ROOT}/etc/named/views/partner/secondary/example-partner.conf" >/dev/null
grep -Rni '203.0.113.0/24' "${RENDER_ROOT}/etc/named/conf.d/00-acl.conf" >/dev/null

bash "${PROJECT_ROOT}/tests/render/check-render-no-placeholders.sh" "${RENDER_ROOT}"

echo "Zone ACL and partner view render validation OK"
