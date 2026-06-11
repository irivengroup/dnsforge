#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

test ! -d "${PROJECT_ROOT}/src/settings"
test -d "${PROJECT_ROOT}/install/templates"

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from pathlib import Path
import tempfile

from dnsforge.application.zone.zone_manager import ZoneManager
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.interfaces.cli.main import build_parser

parser = build_parser()
parser.parse_args(["zone", "show", "example.com"])
parser.parse_args(["zone", "show", "--zone", "example.com", "--version", "1"])
parser.parse_args(["zone", "show", "example.com", "--version", "1"])
parser.parse_args(["zone", "history", "example.com"])

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    manager = ZoneManager(ProjectPaths(root), catalog=ZoneCatalog(root / "zones.yml"))
    manager.create("example.com", "master", ["external"])
    manager.add_record("example.com", "A:www:192.168.10.10")

    active = manager.show("example.com")
    assert "Zone: example.com" in active
    assert "www" in active

    history = manager.history_list("example.com")
    assert "Current Version:" in history

    version = manager.show_version("example.com", 1)
    assert "name: example.com" in version
PY

echo "dnsforge zone show/settings validation OK"
