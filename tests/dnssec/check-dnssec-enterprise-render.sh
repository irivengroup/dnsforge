#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

bash "${PROJECT_ROOT}/tests/integration/render-proxy-multivip.sh"
RENDER_ROOT="${PROJECT_ROOT}/src/render/dns-proxy/multivip"

test -f "${RENDER_ROOT}/etc/named/dnssec/dnssec-policy-enterprise.conf"
grep -q 'dnssec-policy' "${RENDER_ROOT}/etc/named/views/external/master/split-example.invalid.conf"
grep -q 'inline-signing yes' "${RENDER_ROOT}/etc/named/views/external/master/split-example.invalid.conf"

bash "${PROJECT_ROOT}/tests/render/check-render-no-placeholders.sh" "${RENDER_ROOT}"

echo "DNSSEC enterprise render validation OK"
