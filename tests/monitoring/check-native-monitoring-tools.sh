#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

test -x "${PROJECT_ROOT}/src/tools/monitoring/check-binddns-health.sh"
test -x "${PROJECT_ROOT}/src/tools/monitoring/collect-rndc-stats.sh"
test -x "${PROJECT_ROOT}/src/tools/monitoring/export-binddns-metrics-text.sh"

bash -n "${PROJECT_ROOT}/src/tools/monitoring/check-binddns-health.sh"
bash -n "${PROJECT_ROOT}/src/tools/monitoring/collect-rndc-stats.sh"
bash -n "${PROJECT_ROOT}/src/tools/monitoring/export-binddns-metrics-text.sh"

echo "Native monitoring tooling validation OK"
