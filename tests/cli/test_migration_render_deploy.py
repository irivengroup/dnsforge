from __future__ import annotations

from pathlib import Path

import pytest

from dnsforge.application.migration.migration_service import MigrationService
from dnsforge.domain.migration.model import MigrationTarget
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.domain.model.roles import DnsRole
from dnsforge.shared.errors import SettingsError


class _Renderer:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def execute(self, node: str, proxy_type) -> None:  # type: ignore[no-untyped-def]
        self.calls.append((node, proxy_type.value))


class _Deploy:
    def __init__(self) -> None:
        self.calls: list[tuple[Path, Path, bool]] = []

    def deploy(self, render_root: Path, target_root: Path = Path("/"), dry_run: bool = False) -> None:
        self.calls.append((render_root, target_root, dry_run))


def _setup(tmp_path: Path, proxy_type: str = "forwarder") -> Path:
    setup = tmp_path / "etc" / "dnsforge" / "setup.conf"
    setup.parent.mkdir(parents=True)
    setup.write_text(
        "\n".join(
            [
                'ROLE="dns-proxy"',
                'NODE_NAME="proxy01"',
                f'PROXY_TYPE="{proxy_type}"',
                'ENABLE_PROXY_MASTER_ZONES="no"',
                'ENABLE_PROXY_AUTHORITATIVE_ZONES="no"',
                'ENABLE_PROXY_LOCAL_ZONES="no"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return setup


def test_proxy_migration_updates_setup_renders_and_deploys(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    setup = _setup(tmp_path, "forwarder")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(setup.parent))
    monkeypatch.setenv("DNSFORGE_SETUP_FILE", str(setup))
    paths = ProjectPaths(tmp_path)
    renderer = _Renderer()
    deployer = _Deploy()

    result = MigrationService(paths=paths, renderer=renderer, deployer=deployer).migrate(
        setup,
        MigrationTarget.PROXY_HYBRID,
        reason="unit test migration",
        target_root=tmp_path / "target",
    )

    text = setup.read_text(encoding="utf-8")
    assert 'PROXY_TYPE="hybrid"' in text
    assert 'ENABLE_PROXY_MASTER_ZONES="yes"' in text
    assert 'ENABLE_PROXY_AUTHORITATIVE_ZONES="yes"' in text
    assert 'ENABLE_PROXY_LOCAL_ZONES="yes"' in text
    assert renderer.calls == [("proxy01", "hybrid")]
    assert deployer.calls == [(paths.render_dir(DnsRole.PROXY, "proxy01"), tmp_path / "target", False)]
    assert "Migrated proxy-forwarder -> proxy-hybrid" in result
    assert list(setup.parent.glob("setup.conf.backup.*"))


def test_proxy_migration_dry_run_does_not_touch_setup_or_deploy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    setup = _setup(tmp_path, "hybrid")
    original = setup.read_text(encoding="utf-8")
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(setup.parent))
    monkeypatch.setenv("DNSFORGE_SETUP_FILE", str(setup))
    renderer = _Renderer()
    deployer = _Deploy()

    result = MigrationService(paths=ProjectPaths(tmp_path), renderer=renderer, deployer=deployer).migrate(
        setup, MigrationTarget.PROXY_FORWARDER, dry_run=True
    )

    assert setup.read_text(encoding="utf-8") == original
    assert renderer.calls == []
    assert deployer.calls == []
    assert "Would migrate" in result


def test_proxy_migration_requires_reason_for_real_change(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    setup = _setup(tmp_path, "forwarder")
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(setup.parent))
    monkeypatch.setenv("DNSFORGE_SETUP_FILE", str(setup))

    with pytest.raises(SettingsError):
        MigrationService(paths=ProjectPaths(tmp_path), renderer=_Renderer(), deployer=_Deploy()).migrate(
            setup, MigrationTarget.PROXY_HYBRID
        )


def test_proxy_migration_refuses_authoritative_role(tmp_path: Path) -> None:
    setup = tmp_path / "setup.conf"
    setup.write_text('ROLE="dns-authoritative"\nNODE_NAME="auth01"\n', encoding="utf-8")

    with pytest.raises(SettingsError):
        MigrationService(paths=ProjectPaths(tmp_path), renderer=_Renderer(), deployer=_Deploy()).migrate(
            setup, MigrationTarget.PROXY_HYBRID, dry_run=True
        )
