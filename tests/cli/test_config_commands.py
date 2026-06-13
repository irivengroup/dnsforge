from __future__ import annotations

from pathlib import Path

from dnsforge.application.config.config_service import ConfigService
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.interfaces.cli.main import build_parser


def write_setup(path: Path, role: str = "dns-authoritative") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'ROLE="{role}"\nNODE_NAME="node01"\nDNSSEC_ENABLED="yes"\nRPZ_ENABLED="no"\nCLUSTER_ENABLED="no"\n',
        encoding="utf-8",
    )


def test_config_parser_exposes_governance_commands() -> None:
    parser = build_parser()
    for command in (
        ["config", "show"],
        ["config", "validate"],
        ["config", "diff"],
        ["config", "history"],
        ["config", "apply", "--reason", "test"],
        ["config", "rollback", "--id", "1", "--reason", "test"],
        ["audit", "config"],
    ):
        args = parser.parse_args(command)
        assert args.command in {"config", "audit"}


def test_config_history_diff_and_rollback_dry_run(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(tmp_path / "etc/dnsforge"))
    monkeypatch.setenv("DNSFORGE_BACKUP_ROOT", str(tmp_path / "backups"))
    paths = ProjectPaths(tmp_path)
    write_setup(paths.setup_file)
    service = ConfigService(paths)

    first = service.repository.create_snapshot(paths.setup_file.read_text(encoding="utf-8"), "initial")
    paths.setup_file.write_text(
        paths.setup_file.read_text(encoding="utf-8") + 'VIEW_INTERNAL_ENABLED="yes"\n', encoding="utf-8"
    )
    second = service.repository.create_snapshot(paths.setup_file.read_text(encoding="utf-8"), "view")

    history = service.history()
    assert "initial" in history
    assert "view" in history
    assert "VIEW_INTERNAL_ENABLED" in service.diff(identifier=first.identifier)
    assert "VIEW_INTERNAL_ENABLED" in service.diff(id1=first.identifier, id2=second.identifier)
    assert "dry-run" in service.rollback(first.identifier, "test rollback", dry_run=True)


def test_config_audit_detects_invalid_role(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(tmp_path / "etc/dnsforge"))
    paths = ProjectPaths(tmp_path)
    write_setup(paths.setup_file, role="bad-role")
    ok, output = ConfigService(paths).audit()
    assert not ok
    assert "ROLE" in output
