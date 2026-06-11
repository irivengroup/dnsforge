#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from pathlib import Path
import tarfile
import tempfile

from dnsforge.application.initialize.initialize_planner import InitializePlanner
from dnsforge.domain.initialize.plan import InitializePlan
from dnsforge.infrastructure.bind.configuration_backup import BindConfigurationBackup
from dnsforge.infrastructure.bind.layout import BindLayoutDetector
from dnsforge.interfaces.cli.main import build_parser

parser = build_parser()
parser.parse_args(["initialize", "authoritative", "local", "--dry-run"])
parser.parse_args(["initialize", "proxy", "local", "--type", "forwarder", "--dry-run"])

plan = InitializePlanner().build_authoritative_plan("local", Path("/tmp/render"), dry_run=True, backup_before_apply=True)
assert isinstance(plan, InitializePlan)
assert not any(step.name == "install required packages" for step in plan.steps)
assert any(step.name == "backup existing BIND configuration" for step in plan.steps)
assert "python-bind-deployer" in plan.summary()

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "etc/named").mkdir(parents=True)
    (root / "etc/named/old.conf").write_text("// old include\n", encoding="utf-8")
    (root / "etc/named.conf").write_text("// old named\n", encoding="utf-8")
    layout = BindLayoutDetector().from_family("redhat")
    result = BindConfigurationBackup(backup_root=Path("/var/backups/dnsforge/bind-config"), layout=layout).create(target_root=root)
    assert result.archive.exists()
    assert not (root / "etc/named").exists()
    assert not (root / "etc/named.conf").exists()
    with tarfile.open(result.archive, "r:gz") as tar:
        names = set(tar.getnames())
    assert "./etc/named/old.conf" in names
    assert "./etc/named.conf" in names

for family, named_conf, config_dir, data_dir, service in (
    ("redhat", "/etc/named.conf", "/etc/named", "/var/named", "named"),
    ("debian", "/etc/bind/named.conf", "/etc/bind", "/var/lib/bind", "bind9"),
    ("suse", "/etc/named.conf", "/etc/named", "/var/lib/named", "named"),
):
    layout = BindLayoutDetector().from_family(family)
    assert str(layout.named_conf) == named_conf
    assert str(layout.config_dir) == config_dir
    assert str(layout.data_dir) == data_dir
    assert layout.service_name == service
PY

echo "dnsforge initialize BIND deploy validation OK"
