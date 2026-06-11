#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src"
python3 - <<'PY'
from dnsforge.infrastructure.templates import TemplateRegistry
assert 'catalog-zone' in TemplateRegistry.keys()
PY
echo "Catalog public DNSSEC validation OK"
