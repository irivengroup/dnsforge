#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src"
python3 - <<'PY'
from dnsforge.infrastructure.bind.layout import BindLayoutDetector
from dnsforge.infrastructure.rendering.bind_renderer import BindConfigFactory
layout = BindLayoutDetector().from_family('redhat')
factory = BindConfigFactory()
assert 'RPZ is disabled' in factory.rpz_with_layout({'ENABLE_RPZ': 'no'}, layout) or factory.rpz_with_layout({'ENABLE_RPZ': 'no'}, layout) == ''
PY
echo "RPZ authoritative render clean OK"
