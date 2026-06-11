#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src"
python3 - <<'PY'
from dnsforge.infrastructure.bind.layout import BindLayoutDetector
from dnsforge.infrastructure.rendering.bind_renderer import BindConfigFactory
layout = BindLayoutDetector().from_family('redhat')
factory = BindConfigFactory()
master = factory.master_template(layout, 'internal')
assert 'type master;' in master
assert '/var/named/master/internal' in master
PY
echo "Proxy master zone validation OK"
