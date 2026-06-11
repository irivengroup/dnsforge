#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src"
python3 - <<'PY'
from dnsforge.infrastructure.bind.layout import BindLayoutDetector
from dnsforge.infrastructure.rendering.bind_renderer import BindConfigFactory
layout = BindLayoutDetector().from_family('redhat')
factory = BindConfigFactory()
rpz = factory.rpz_with_layout({'ENABLE_RPZ': 'yes', 'RPZ_ZONE_NAME': 'rpz.local'}, layout)
views = factory.views(layout)
assert '/var/named/rpz/rpz.local.zone' in rpz
assert 'zones.index.conf' in views
assert '/etc/named/conf.d/50-rpz.conf' not in factory.named_conf(layout, False, True)
PY
echo "RPZ coherence OK"
