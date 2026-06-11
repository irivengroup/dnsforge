#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src"
python3 - <<'PY'
from dnsforge.infrastructure.rendering.bind_renderer import BindConfigFactory
from dnsforge.infrastructure.bind.layout import BindLayoutDetector
factory = BindConfigFactory()
layout = BindLayoutDetector().from_family('redhat')
content = factory.authoritative_options({'SECURITY_PROFILE': 'enterprise'}, layout)
assert 'dnssec-validation auto;' in content
PY
echo "DNSSEC template validation OK"
