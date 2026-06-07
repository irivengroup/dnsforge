#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cp "${PROJECT_ROOT}/tests/fixtures/settings/dns-proxy/multivip.env" "${PROJECT_ROOT}/src/settings/dns-proxy/multivip.env"
cleanup(){ rm -f "${PROJECT_ROOT}/src/settings/dns-proxy/multivip.env"; }
trap cleanup EXIT
"${PROJECT_ROOT}/src/tools/generate-zone-catalog.sh"
"${PROJECT_ROOT}/src/dnsProxyDeploy.sh" multivip --render-only
echo "Rendered multivip proxy fixture"
