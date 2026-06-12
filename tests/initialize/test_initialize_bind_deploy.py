from __future__ import annotations

import tarfile
from pathlib import Path

from dnsforge.application.initialize.initialize_planner import InitializePlanner
from dnsforge.domain.initialize.plan import InitializePlan
from dnsforge.infrastructure.bind.configuration_backup import BindConfigurationBackup
from dnsforge.infrastructure.bind.layout import BindLayoutDetector
from dnsforge.interfaces.cli.main import build_parser


def test_initialize_plan_backs_up_bind_without_installing_packages() -> None:
    parser = build_parser()
    parser.parse_args(["initialize", "authoritative", "local", "--dry-run"])
    parser.parse_args(["initialize", "proxy", "local", "--type", "forwarder", "--dry-run"])

    plan = InitializePlanner().build_authoritative_plan("local", Path("/tmp/render"), dry_run=True, backup_before_apply=True)
    assert isinstance(plan, InitializePlan)
    assert not any(step.name == "install required packages" for step in plan.steps)
    assert any(step.name == "backup existing BIND configuration" for step in plan.steps)
    assert "python-bind-deployer" in plan.summary()


def test_bind_configuration_backup_moves_and_archives_existing_config(tmp_path: Path) -> None:
    root = tmp_path
    (root / "etc/named").mkdir(parents=True)
    (root / "etc/named/old.conf").write_text("// old include\n", encoding="utf-8")
    (root / "etc/named.conf").write_text("// old named\n", encoding="utf-8")
    layout = BindLayoutDetector().from_family("redhat")
    result = BindConfigurationBackup(backup_root=tmp_path / "backups", layout=layout).create(target_root=root)
    assert result.archive.exists()
    assert not (root / "etc/named").exists()
    assert not (root / "etc/named.conf").exists()
    with tarfile.open(result.archive, "r:gz") as tar:
        names = set(tar.getnames())
    assert "./etc/named/old.conf" in names
    assert "./etc/named.conf" in names


def test_bind_layouts_match_distribution_paths() -> None:
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
