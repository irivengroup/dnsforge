from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from dnsforge.domain.zone.model import ZoneDefinition, ZoneType
from dnsforge.interfaces.cli.application import DnsForgeArgumentParserFactory, DnsForgeCommandDispatcher


@dataclass
class _Report:
    ok: bool = True
    findings: list[str] | None = None

    def render(self) -> str:
        return "OK"


class _Executable:
    def __init__(self, *_args, **_kwargs) -> None:
        pass

    def execute(self, *_args, **_kwargs) -> str:
        return "OK"


class _Deploy:
    def deploy(self, *_args, **_kwargs) -> str:
        return "OK"


class _ProductAuditor:
    def audit(self, *_args, **_kwargs) -> _Report:
        return _Report(findings=[])


class _ProfileAuditor:
    def audit_templates(self, *_args, **_kwargs) -> list[str]:
        return []


class _SecurityService:
    def show(self, *_args, **_kwargs) -> str:
        return "OK"

    def audit(self, *_args, **_kwargs) -> tuple[bool, str]:
        return True, "OK"


class _SecurityHistoryService:
    def history(self) -> str:
        return "OK"

    def rollback(self, *_args, **_kwargs) -> str:
        return "OK"


class _StatusService:
    def show(self, *_args, **_kwargs) -> str:
        return "OK"


class _HealthService:
    def check(self, *_args, **_kwargs) -> _Report:
        return _Report()


class _DoctorService:
    def diagnose(self, *_args, **_kwargs) -> str:
        return "OK"


class _BackupService:
    def __init__(self, *_args, **_kwargs) -> None:
        pass

    def create(self, *_args, **_kwargs) -> str:
        return "backup.tar.gz"

    def list(self) -> list[str]:
        return ["backup.tar.gz"]

    def restore(self, *_args, **_kwargs) -> None:
        return None


class _MigrationService:
    def migrate(self, *_args, **_kwargs) -> str:
        return "OK"


class _ClusterService:
    def init(self, *_args, **_kwargs) -> str:
        return "OK"

    def status(self, *_args, **_kwargs) -> str:
        return "OK"

    def validate(self, *_args, **_kwargs) -> str:
        return "OK"

    def validate_security(self, *_args, **_kwargs) -> str:
        return "OK"

    def sync(self, *_args, **_kwargs) -> str:
        return "OK"


class _AclService:
    def __init__(self, *_args, **_kwargs) -> None:
        pass

    def list(self) -> str:
        return "OK"

    def show(self, *_args, **_kwargs) -> str:
        return "OK"

    def create(self, *_args, **_kwargs) -> str:
        return "OK"

    def delete(self, *_args, **_kwargs) -> str:
        return "OK"

    def add_network(self, *_args, **_kwargs) -> str:
        return "OK"

    def remove_network(self, *_args, **_kwargs) -> str:
        return "OK"


class _ViewService:
    def __init__(self, *_args, **_kwargs) -> None:
        pass

    def list(self) -> str:
        return "OK"

    def create(self, *_args, **_kwargs) -> str:
        return "OK"

    def delete(self, *_args, **_kwargs) -> str:
        return "OK"

    def attach_zone(self, *_args, **_kwargs) -> str:
        return "OK"


class _DnssecService:
    def status(self, *_args, **_kwargs) -> str:
        return "OK"

    def validate(self, *_args, **_kwargs) -> str:
        return "OK"

    def rotate_ksk(self) -> str:
        return "OK"

    def rotate_zsk(self) -> str:
        return "OK"

    def check_expiry(self) -> str:
        return "OK"


class _RpzService:
    def status(self, *_args, **_kwargs) -> str:
        return "OK"

    def enable(self, *_args, **_kwargs) -> str:
        return "OK"

    def update(self) -> str:
        return "OK"

    def test(self, *_args, **_kwargs) -> str:
        return "OK"


class _ZoneManager:
    def __init__(self, *_args, **_kwargs) -> None:
        self.zone = ZoneDefinition("example.com", ZoneType.MASTER, ["external"])

    def list(self) -> list[ZoneDefinition]:
        return [self.zone]

    def get(self, *_args, **_kwargs) -> ZoneDefinition:
        return self.zone

    def history_list(self, *_args, **_kwargs) -> str:
        return "OK"

    def show(self, *_args, **_kwargs) -> str:
        return "OK"

    def show_version(self, *_args, **_kwargs) -> str:
        return "OK"

    def history_diff(self, *_args, **_kwargs) -> str:
        return "OK"

    def rollback(self, *_args, **_kwargs) -> str:
        return "OK"

    def create(self, *_args, **_kwargs) -> None:
        return None

    def add_record(self, *_args, **_kwargs) -> None:
        return None

    def update_record(self, *_args, **_kwargs) -> None:
        return None

    def delete_record(self, *_args, **_kwargs) -> None:
        return None

    def disable(self, *_args, **_kwargs) -> None:
        return None

    def enable(self, *_args, **_kwargs) -> None:
        return None

    def delete(self, *_args, **_kwargs) -> None:
        return None


@pytest.fixture(autouse=True)
def _patch_services(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from dnsforge.interfaces.cli import application as app

    setup_file = tmp_path / "setup.conf"
    setup_file.write_text("ROLE=dns-proxy\nNODE_NAME=proxy01\nPROXY_TYPE=forwarder\n", encoding="utf-8")
    monkeypatch.setenv("DNSFORGE_SETUP_FILE", str(setup_file))
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(tmp_path))
    monkeypatch.setattr(app, "ValidateProxy", _Executable)
    monkeypatch.setattr(app, "ValidateAuthoritative", _Executable)
    monkeypatch.setattr(app, "RenderProxy", _Executable)
    monkeypatch.setattr(app, "RenderAuthoritative", _Executable)
    monkeypatch.setattr(app, "InitializeProxy", _Executable)
    monkeypatch.setattr(app, "InitializeAuthoritative", _Executable)
    monkeypatch.setattr(app, "DeployService", _Deploy)
    monkeypatch.setattr(app, "ZoneManager", _ZoneManager)
    monkeypatch.setattr(app, "ProductAuditor", _ProductAuditor)
    monkeypatch.setattr(app, "ProfileAuditor", _ProfileAuditor)
    monkeypatch.setattr(app, "SecurityService", _SecurityService)
    monkeypatch.setattr(app, "SecurityHistoryService", _SecurityHistoryService)
    monkeypatch.setattr(app, "StatusService", _StatusService)
    monkeypatch.setattr(app, "HealthService", _HealthService)
    monkeypatch.setattr(app, "DoctorService", _DoctorService)
    monkeypatch.setattr(app, "BackupService", _BackupService)
    monkeypatch.setattr(app, "MigrationService", _MigrationService)
    monkeypatch.setattr(app, "ClusterService", _ClusterService)
    monkeypatch.setattr(app, "AclService", _AclService)
    monkeypatch.setattr(app, "ViewService", _ViewService)
    monkeypatch.setattr(app, "DnssecService", _DnssecService)
    monkeypatch.setattr(app, "RpzService", _RpzService)


CLI_COMMANDS: list[list[str]] = [
    ["validate"],
    ["validate", "proxy", "proxy01", "--type", "forwarder"],
    ["validate", "proxy", "proxy01", "--type", "hybrid"],
    ["validate", "authoritative", "auth01"],
    ["render"],
    ["render", "proxy", "proxy01", "--type", "forwarder"],
    ["render", "proxy", "proxy01", "--type", "hybrid"],
    ["render", "authoritative", "auth01"],
    ["deploy", "--dry-run"],
    ["deploy", "proxy", "proxy01", "--type", "forwarder", "--target-root", "/tmp", "--dry-run"],
    ["deploy", "authoritative", "auth01", "--target-root", "/tmp", "--dry-run"],
    ["authoritative", "initialize", "--render-only"],
    ["authoritative", "initialize", "--apply", "--dry-run"],
    ["proxy", "initialize", "proxy01", "--type", "forwarder", "--render-only"],
    ["proxy", "initialize", "proxy01", "--type", "hybrid", "--dry-run"],
    ["authoritative", "initialize", "auth01", "--render-only"],
    ["zone", "list"],
    ["zone", "get", "--name", "example.com"],
    ["zone", "show", "example.com"],
    ["zone", "show", "--zone", "example.com", "--version", "1"],
    ["zone", "history", "example.com"],
    ["zone", "diff", "--zone", "example.com", "--from", "1", "--to", "2"],
    ["zone", "rollback", "--zone", "example.com", "--version", "1"],
    ["zone", "create", "--name", "example.com", "--type", "master", "--views", "external,internal"],
    ["zone", "create", "--name", "example.net", "--type", "secondary", "--views", "external", "--disabled"],
    ["zone", "edit", "example.com", "--add", "A:www:192.0.2.10", "--ttl", "300"],
    ["zone", "edit", "example.com", "--update", "A:www:192.0.2.11", "--ttl", "300"],
    ["zone", "edit", "example.com", "--delete", "A:www:192.0.2.10"],
    ["zone", "enable", "--name", "example.com"],
    ["zone", "disable", "--name", "example.com"],
    ["zone", "delete", "--name", "example.com"],
    ["audit"],
    ["audit", "--strict"],
    ["profile", "audit"],
    ["security", "show"],
    ["security", "audit"],
    ["security", "history"],
    ["security", "rollback", "--version", "1"],
    ["status"],
    ["health"],
    ["doctor"],
    ["backup", "create", "--dry-run"],
    ["backup", "list"],
    ["restore", "--backup", "backup.tar.gz", "--target-root", "/tmp", "--dry-run"],
    ["migrate", "--to", "proxy-forwarder", "--dry-run"],
    ["migrate", "--to", "proxy-hybrid", "--dry-run"],
    ["cluster", "init", "--dry-run"],
    ["cluster", "status"],
    ["cluster", "validate"],
    ["cluster", "validate-security"],
    ["cluster", "sync", "--dry-run"],
    ["acl", "list"],
    ["acl", "show", "trusted"],
    ["acl", "create", "trusted"],
    ["acl", "delete", "trusted"],
    ["acl", "add-network", "trusted", "192.0.2.0/24"],
    ["acl", "remove-network", "trusted", "192.0.2.0/24"],
    ["view", "list"],
    ["view", "create", "internal"],
    ["view", "delete", "internal"],
    ["view", "attach-zone", "internal", "example.com"],
    ["dnssec", "status"],
    ["dnssec", "validate"],
    ["dnssec", "rotate-ksk"],
    ["dnssec", "rotate-zsk"],
    ["dnssec", "check-expiry"],
    ["rpz", "status"],
    ["rpz", "enable"],
    ["rpz", "update"],
    ["rpz", "test", "malware.example"],
]


@pytest.mark.parametrize("argv", CLI_COMMANDS)
def test_every_exposed_cli_form_is_parsed_and_dispatched(argv: list[str], tmp_path: Path) -> None:
    parser = DnsForgeArgumentParserFactory().build()
    args = parser.parse_args(["--project-root", str(tmp_path), *argv])
    assert DnsForgeCommandDispatcher().dispatch(args) in {0, 1}


def test_initialize_render_only_and_apply_are_mutually_exclusive(tmp_path: Path) -> None:
    parser = DnsForgeArgumentParserFactory().build()
    args = parser.parse_args(
        ["--project-root", str(tmp_path), "authoritative", "initialize", "--render-only", "--apply"]
    )
    assert DnsForgeCommandDispatcher().dispatch(args) == 2
