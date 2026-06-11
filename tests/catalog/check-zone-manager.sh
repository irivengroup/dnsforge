#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT
python3 - <<'PY' "${TMP_DIR}/zones.yml"
from pathlib import Path
from dnsforge.domain.zone.model import ZoneDefinition, ZoneType
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
catalog = ZoneCatalog(Path(__import__('sys').argv[1]))
catalog.create(ZoneDefinition('example.com', ZoneType.MASTER, ['external'], enabled=True))
assert catalog.get('example.com').enabled
catalog.disable('example.com')
assert not catalog.get('example.com').enabled
catalog.enable('example.com')
assert catalog.get('example.com').enabled
PY
echo "Zone manager OK"
