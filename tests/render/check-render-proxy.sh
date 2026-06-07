#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
NODE="${1:-}"

if [[ -z "${NODE}" ]]
then
    echo "Usage: $0 <proxy-node>" >&2
    exit 1
fi

"${PROJECT_ROOT}/src/dnsProxyDeploy.sh" "${NODE}" --render-only

RENDER_NODE="${PROJECT_ROOT}/src/render/dns-proxy/${NODE}"

bash "${PROJECT_ROOT}/tests/render/check-render-paths.sh" "${PROJECT_ROOT}/src/render"
bash "${PROJECT_ROOT}/tests/render/check-render-no-placeholders.sh" "${RENDER_NODE}"
bash "${PROJECT_ROOT}/tests/dns-validation/check-zone-indexes.sh"
bash "${PROJECT_ROOT}/tests/project/check-rpz-coherence.sh"

echo "DNS proxy render validation OK for ${NODE}"
