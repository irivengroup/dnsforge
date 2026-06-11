#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src"
python3 - <<'PY'
from pathlib import Path
from dnsforge.infrastructure.bind.rendering import TemplateRegistry
root = Path('src/dnsforge/infrastructure/bind/resources')
for template in TemplateRegistry.templates():
    path = root / template
    assert path.exists(), f'missing registered template: {template}'
    content = path.read_text(encoding='utf-8')
    assert '/etc/dnsforge/generated' not in content
    assert '/var/lib/dnsforge' not in content
PY
echo "BIND template formatting OK"
