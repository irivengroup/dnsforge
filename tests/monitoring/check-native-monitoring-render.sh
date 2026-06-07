#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

bash "${PROJECT_ROOT}/tests/integration/render-proxy-multivip.sh"
RENDER_ROOT="${PROJECT_ROOT}/src/render/dns-proxy/multivip"

test -x "${RENDER_ROOT}/opt/binddns/monitoring/check-binddns-health.sh"
test -x "${RENDER_ROOT}/opt/binddns/monitoring/collect-rndc-stats.sh"
test -x "${RENDER_ROOT}/opt/binddns/monitoring/export-binddns-metrics-text.sh"
test -f "${RENDER_ROOT}/opt/binddns/monitoring/systemd/binddns-healthcheck.service"
test -f "${RENDER_ROOT}/opt/binddns/monitoring/systemd/binddns-healthcheck.timer"

grep -Rni 'ExecStart=/opt/binddns/monitoring/check-binddns-health.sh' "${RENDER_ROOT}/opt/binddns/monitoring/systemd" >/dev/null
bash "${PROJECT_ROOT}/tests/render/check-render-no-placeholders.sh" "${RENDER_ROOT}"

echo "Native monitoring render validation OK"
