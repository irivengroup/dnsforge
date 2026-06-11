#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src"
python3 - <<'PY'
from dnsforge.infrastructure.templates import TemplateRegistry
required = {'named.conf', 'options', 'views', 'external-master-template', 'internal-master-template'}
assert required.issubset(set(TemplateRegistry.keys()))
PY
echo "DNSSEC enterprise template validation OK"
