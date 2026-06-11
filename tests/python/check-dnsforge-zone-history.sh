#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from pathlib import Path
import tempfile
from dnsforge.application.zone.zone_manager import ZoneManager
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.interfaces.cli.main import build_parser

p=build_parser()
p.parse_args(["zone","history","example.com"])
p.parse_args(["zone","show","example.com","--version","1"])
p.parse_args(["zone","diff","--zone","example.com","--from","1","--to","2"])
p.parse_args(["zone","rollback","--zone","example.com","--version","1"])

with tempfile.TemporaryDirectory() as tmp:
    r=Path(tmp)
    m=ZoneManager(ProjectPaths(r), catalog=ZoneCatalog(r/"zones.yml"))
    m.create("example.com","master",["external"])
    m.add_record("example.com","A:www:192.168.10.10")
    m.update_record("example.com","A:www:192.168.10.10:192.168.10.20")
    h=m.history_list("example.com")
    assert "create" in h and "add-record" in h and "update-record" in h
    assert "example.com@1" in m.history_diff("example.com",1,2)
    assert "Rollback completed" in m.rollback("example.com",1)
PY
echo "dnsforge zone history validation OK"
