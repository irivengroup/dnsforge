#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
bash "${PROJECT_ROOT}/tests/integration/render-proxy-multivip.sh"
bash "${PROJECT_ROOT}/tests/integration/check-forwarders-multivip.sh"
bash "${PROJECT_ROOT}/tests/integration/check-primaries-multivip.sh"
bash "${PROJECT_ROOT}/tests/integration/check-allow-notify-multivip.sh"
bash "${PROJECT_ROOT}/tests/render/check-render-no-placeholders.sh" "${PROJECT_ROOT}/src/render/dns-proxy/multivip"
bash "${PROJECT_ROOT}/tests/dns-validation/check-zone-indexes.sh"
echo "Proxy multi-VIP integration validation OK"
