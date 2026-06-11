#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src"
python3 - <<'PY'
from dnsforge.infrastructure.bind.layout import BindLayoutDetector
layout = BindLayoutDetector().from_family('redhat')
assert str(layout.log_dir) == '/var/log/named'
assert str(layout.statistics_data_dir).endswith('/data')
PY
echo "Monitoring template validation OK"
