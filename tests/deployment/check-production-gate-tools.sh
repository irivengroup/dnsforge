#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

test -x "${PROJECT_ROOT}/src/tools/deployment/diff-rendered-config.sh"
test -x "${PROJECT_ROOT}/src/tools/deployment/preflight-production-gate.sh"
test -x "${PROJECT_ROOT}/src/tools/deployment/rollback-latest.sh"

bash -n "${PROJECT_ROOT}/src/tools/deployment/diff-rendered-config.sh"
bash -n "${PROJECT_ROOT}/src/tools/deployment/preflight-production-gate.sh"
bash -n "${PROJECT_ROOT}/src/tools/deployment/rollback-latest.sh"

echo "Production gate tooling validation OK"
