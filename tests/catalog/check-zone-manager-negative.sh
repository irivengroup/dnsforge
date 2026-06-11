#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT
python3 - <<'PY' "${TMP_DIR}/zones.yml"
from pathlib import Path
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.shared.errors import ZoneError
catalog = ZoneCatalog(Path(__import__('sys').argv[1]))
try:
    catalog.get('missing.example')
except ZoneError:
    pass
else:
    raise AssertionError('missing zone must raise ZoneError')
PY
echo "Zone manager negative OK"
