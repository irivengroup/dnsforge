#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

bash "${PROJECT_ROOT}/tests/integration/render-proxy-multivip.sh"
RENDER_ROOT="${PROJECT_ROOT}/src/render/dns-proxy/multivip"

grep -Rni 'corp-a-public.invalid' "${RENDER_ROOT}/etc/named" >/dev/null
grep -Rni '192.0.2.10 key "xfr-shared-key";' "${RENDER_ROOT}/etc/named" >/dev/null

grep -Rni 'corp-b-public.invalid' "${RENDER_ROOT}/etc/named" >/dev/null
grep -Rni '192.0.2.20 key "xfr-shared-key";' "${RENDER_ROOT}/etc/named" >/dev/null
grep -Rni '192.0.2.21 key "xfr-shared-key";' "${RENDER_ROOT}/etc/named" >/dev/null

grep -Rni 'corp-a-forward.invalid' "${RENDER_ROOT}/etc/named" >/dev/null
grep -Rni 'corp-b-forward.invalid' "${RENDER_ROOT}/etc/named" >/dev/null

bash "${PROJECT_ROOT}/tests/render/check-render-no-placeholders.sh" "${RENDER_ROOT}"
echo "Zone-to-authoritative-cluster routing validation OK"
