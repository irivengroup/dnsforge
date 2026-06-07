#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

test -f "${PROJECT_ROOT}/src/build/common/monitoring/prometheus/bind-exporter.service.tpl"
test -f "${PROJECT_ROOT}/src/build/common/monitoring/prometheus/prometheus-scrape-bind.yml.tpl"
test -f "${PROJECT_ROOT}/src/build/common/monitoring/telegraf/telegraf-binddns.conf.tpl"
test -f "${PROJECT_ROOT}/src/build/common/monitoring/grafana/binddns-dashboard-notes.md"

grep -Rni '{{ ADM_IP }}' "${PROJECT_ROOT}/src/build/common/monitoring" >/dev/null
grep -Rni '{{ NODE_NAME }}' "${PROJECT_ROOT}/src/build/common/monitoring" >/dev/null
grep -Rni '{{ ROLE }}' "${PROJECT_ROOT}/src/build/common/monitoring" >/dev/null

echo "Monitoring template validation OK"
