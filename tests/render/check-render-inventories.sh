#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

failed=0

for inventory in "${PROJECT_ROOT}"/src/settings/dns-proxy/*.env
do
    node="$(basename "${inventory}" .env)"
    echo "Rendering proxy inventory: ${node}"
    if ! "${PROJECT_ROOT}/src/dnsProxyDeploy.sh" "${node}" --render-only
    then
        failed=1
    fi
done

for inventory in "${PROJECT_ROOT}"/src/settings/dns-authoritative/*.env
do
    node="$(basename "${inventory}" .env)"
    echo "Rendering authoritative inventory: ${node}"
    if ! "${PROJECT_ROOT}/src/dnsAuthoritativeDeploy.sh" "${node}" --render-only
    then
        failed=1
    fi
done

[[ "${failed}" -eq 0 ]] || exit 1

bash "${PROJECT_ROOT}/tests/render/check-render-paths.sh"
bash "${PROJECT_ROOT}/tests/render/check-render-no-placeholders.sh"
bash "${PROJECT_ROOT}/tests/dns-validation/check-zone-indexes.sh"

echo "All inventory render validations OK"
