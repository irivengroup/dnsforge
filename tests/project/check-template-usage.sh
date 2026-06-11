#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src"
python3 - <<'PY'
from pathlib import Path
from dnsforge.infrastructure.bind.rendering import TemplateRegistry
root = Path('src/dnsforge/infrastructure/bind/resources')
assert not (root / 'templates').exists(), 'infrastructure/bind/resources/templates is forbidden'
assert not Path('src/dnsforge/infrastructure/build').exists(), 'infrastructure/build is forbidden'
actual = {p.relative_to(root) for p in root.rglob('*') if p.suffix in {'.j2', '.tpl'}}
registered = set(TemplateRegistry.templates())
assert actual == registered, f'unregistered or missing templates: actual={actual} registered={registered}'
PY
echo "Template usage validation OK"
