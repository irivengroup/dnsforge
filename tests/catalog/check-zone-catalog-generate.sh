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
catalog.save([
    ZoneDefinition('split-example.invalid', ZoneType.MASTER, ['external','internal'], enabled=True),
    ZoneDefinition('catalog-secondary-a.invalid', ZoneType.SECONDARY, ['external'], cluster='AUTH_CLUSTER_A', enabled=True),
])
assert len(catalog.list()) == 2
PY
echo "Zone catalog generation OK"
