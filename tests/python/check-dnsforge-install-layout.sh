#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

test -x "${PROJECT_ROOT}/install/install.sh"
test -x "${PROJECT_ROOT}/install/create-node-settings.sh"
test -f "${PROJECT_ROOT}/install/templates/authoritative/setup.conf"
test -f "${PROJECT_ROOT}/install/templates/proxy-forwarder/setup.conf"
test -f "${PROJECT_ROOT}/install/templates/proxy-hybrid/setup.conf"

grep -q 'ROLE="dns-authoritative"' "${PROJECT_ROOT}/install/templates/authoritative/setup.conf"
grep -q 'PROXY_TYPE="forwarder"' "${PROJECT_ROOT}/install/templates/proxy-forwarder/setup.conf"
grep -q 'PROXY_TYPE="hybrid"' "${PROJECT_ROOT}/install/templates/proxy-hybrid/setup.conf"

bash "${PROJECT_ROOT}/install/install.sh" --help >/dev/null
bash "${PROJECT_ROOT}/install/create-node-settings.sh" --help >/dev/null

echo "dnsforge install layout validation OK"
