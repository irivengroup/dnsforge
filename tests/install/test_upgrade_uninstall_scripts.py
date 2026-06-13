from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPGRADE_SCRIPT = PROJECT_ROOT / "install" / "upgrade.sh"
UNINSTALL_SCRIPT = PROJECT_ROOT / "install" / "uninstall.sh"


def _fake_runtime_path(tmp_path: Path) -> Path:
    bindir = tmp_path / "fake-bin"
    bindir.mkdir(parents=True)
    python3 = bindir / "python3"
    python3.write_text('#!/usr/bin/env sh\nexec python "$@"\n', encoding="utf-8")
    python3.chmod(0o755)
    return bindir


def _env_with_fake_runtime(tmp_path: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{_fake_runtime_path(tmp_path)}:{env['PATH']}"
    return env


def _run(command: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=PROJECT_ROOT, env=env, text=True, capture_output=True, check=True)


@pytest.mark.skipif(os.geteuid() != 0, reason="install maintenance scripts intentionally require root")
def test_upgrade_script_source_mode_creates_backup_and_entrypoint(tmp_path: Path) -> None:
    install_root = tmp_path / "opt" / "dnsforge"
    config_root = tmp_path / "etc" / "dnsforge"
    backup_root = tmp_path / "backups"
    bin_link = tmp_path / "bin" / "dnsforge"
    bin_link.parent.mkdir(parents=True)
    install_root.mkdir(parents=True)
    config_root.mkdir(parents=True)
    (config_root / "setup.conf").write_text('ROLE="dns-authoritative"\n', encoding="utf-8")

    _run(
        [
            "bash",
            str(UPGRADE_SCRIPT),
            "--source",
            "--install-root",
            str(install_root),
            "--config-root",
            str(config_root),
            "--backup-root",
            str(backup_root),
            "--bin-link",
            str(bin_link),
        ],
        env=_env_with_fake_runtime(tmp_path),
    )

    assert bin_link.is_symlink()
    assert bin_link.resolve() == install_root / "bin" / "dnsforge-system"
    assert (install_root / "src" / "dnsforge").is_dir()
    assert list((backup_root / "upgrade").glob("dnsforge-upgrade-*.tar.gz"))


@pytest.mark.skipif(os.geteuid() != 0, reason="install maintenance scripts intentionally require root")
def test_upgrade_script_dry_run_accepts_wheel_without_installing(tmp_path: Path) -> None:
    wheel = tmp_path / "dnsforge-99.0.0-py3-none-any.whl"
    wheel.write_text("fake", encoding="utf-8")
    install_root = tmp_path / "opt" / "dnsforge"
    bin_link = tmp_path / "bin" / "dnsforge"

    result = _run(
        [
            "bash",
            str(UPGRADE_SCRIPT),
            "--wheel",
            str(wheel),
            "--install-root",
            str(install_root),
            "--backup-root",
            str(tmp_path / "backups"),
            "--bin-link",
            str(bin_link),
            "--dry-run",
        ]
    )

    assert "DRY-RUN" in result.stdout
    assert not bin_link.exists()


@pytest.mark.skipif(os.geteuid() != 0, reason="install maintenance scripts intentionally require root")
def test_uninstall_default_removes_product_but_keeps_config_and_bind(tmp_path: Path) -> None:
    install_root = tmp_path / "opt" / "dnsforge"
    config_root = tmp_path / "etc" / "dnsforge"
    backup_root = tmp_path / "backups"
    bin_link = tmp_path / "bin" / "dnsforge"
    install_root.mkdir(parents=True)
    config_root.mkdir(parents=True)
    bin_link.parent.mkdir(parents=True)
    (install_root / "marker").write_text("installed", encoding="utf-8")
    (config_root / "setup.conf").write_text('ROLE="dns-authoritative"\n', encoding="utf-8")
    bin_link.symlink_to(install_root / "marker")

    result = _run(
        [
            "bash",
            str(UNINSTALL_SCRIPT),
            "--install-root",
            str(install_root),
            "--config-root",
            str(config_root),
            "--backup-root",
            str(backup_root),
            "--bin-link",
            str(bin_link),
        ]
    )

    assert not install_root.exists()
    assert not bin_link.exists()
    assert config_root.exists()
    assert "Keeping BIND packages" in result.stdout
    assert list((backup_root / "uninstall").glob("dnsforge-uninstall-*.tar.gz"))


@pytest.mark.skipif(os.geteuid() != 0, reason="install maintenance scripts intentionally require root")
def test_uninstall_purge_removes_config_after_backup(tmp_path: Path) -> None:
    install_root = tmp_path / "opt" / "dnsforge"
    config_root = tmp_path / "etc" / "dnsforge"
    backup_root = tmp_path / "backups"
    install_root.mkdir(parents=True)
    config_root.mkdir(parents=True)
    (config_root / "setup.conf").write_text('ROLE="proxy-hybrid"\n', encoding="utf-8")

    _run(
        [
            "bash",
            str(UNINSTALL_SCRIPT),
            "--install-root",
            str(install_root),
            "--config-root",
            str(config_root),
            "--backup-root",
            str(backup_root),
            "--bin-link",
            str(tmp_path / "bin" / "dnsforge"),
            "--purge",
        ]
    )

    assert not install_root.exists()
    assert not config_root.exists()
    assert list((backup_root / "uninstall").glob("dnsforge-uninstall-*.tar.gz"))


def test_install_directory_exposes_only_supported_entrypoints() -> None:
    scripts = sorted(path.name for path in (PROJECT_ROOT / "install").glob("*.sh"))
    assert scripts == ["install.sh", "uninstall.sh", "upgrade.sh"]
