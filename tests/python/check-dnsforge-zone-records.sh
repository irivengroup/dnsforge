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
from dnsforge.application.zone.zone_manager import ZoneManager
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.interfaces.cli.main import build_parser

parser=build_parser()
parser.parse_args(["zone","show","example.com"])
parser.parse_args(["zone","edit","example.com","--add","A:www:192.168.10.10"])
parser.parse_args(["zone","edit","example.com","--update","A:www:192.168.10.10:192.168.10.15"])
parser.parse_args(["zone","edit","example.com","--delete","A:www"])
with tempfile.TemporaryDirectory() as tmp:
    catalog=ZoneCatalog(Path(tmp)/"zones.yml")
    m=ZoneManager(ProjectPaths(Path(tmp)), catalog=catalog)
    catalog.create(ZoneDefinition("example.com", ZoneType.MASTER, ["external"]))
    m.add_record("example.com","A:www:192.168.10.10",ttl=300)
    assert "www 300 IN A 192.168.10.10" in m.show("example.com")
    m.update_record("example.com","A:www:192.168.10.10:192.168.10.15",ttl=300)
    assert "192.168.10.15" in m.show("example.com")
    m.delete_record("example.com","A:www")
    assert "none" in m.show("example.com")
PY
echo "dnsforge zone records validation OK"
