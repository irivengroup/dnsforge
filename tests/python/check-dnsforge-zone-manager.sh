#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from pathlib import Path
import tempfile

from dnsforge.domain.zone.model import ZoneDefinition, ZoneType
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.interfaces.cli.main import build_parser

parser = build_parser()
parser.parse_args(["zone", "list"])
parser.parse_args(["zone", "get", "--name", "example.com"])
parser.parse_args(["zone", "create", "--name", "example.com", "--type", "master", "--views", "external,internal"])
parser.parse_args(["zone", "disable", "--name", "example.com"])
parser.parse_args(["zone", "enable", "--name", "example.com"])
parser.parse_args(["zone", "delete", "--name", "example.com"])

with tempfile.TemporaryDirectory() as tmp:
    catalog_path = Path(tmp) / "zones.yml"
    catalog = ZoneCatalog(catalog_path)
    zone = ZoneDefinition(
        name="example.test",
        zone_type=ZoneType.MASTER,
        views=["external", "internal"],
        cluster="A",
    )
    catalog.create(zone)
    assert [item.name for item in catalog.list()] == ["example.test"]
    assert catalog.get("example.test").zone_type.value == "master"
    catalog.disable("example.test")
    assert catalog.get("example.test").enabled is False
    catalog.enable("example.test")
    assert catalog.get("example.test").enabled is True
    catalog.delete("example.test")
    assert len(catalog.list()) == 0
PY

echo "dnsforge zone manager validation OK"
