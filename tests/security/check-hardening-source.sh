#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src"
python3 - <<'PY'
from dnsforge.infrastructure.bind.layout import BindLayoutDetector
layout = BindLayoutDetector().from_family('redhat')
assert layout.systemd_override_dir is not None
assert str(layout.systemd_override_dir).endswith('/named.service.d')
PY
echo "Hardening source validation OK"
