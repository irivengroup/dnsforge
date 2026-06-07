#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

bash "${PROJECT_ROOT}/tests/integration/render-proxy-multivip.sh"

RENDER_ROOT="${PROJECT_ROOT}/src/render/dns-proxy/multivip"

bash "${PROJECT_ROOT}/src/tools/deployment/preflight-production-gate.sh" "${RENDER_ROOT}"
bash "${PROJECT_ROOT}/src/tools/deployment/diff-rendered-config.sh" "${RENDER_ROOT}" >/dev/null || true

echo "Production gate render validation OK"
