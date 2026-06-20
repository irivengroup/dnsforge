from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INSTALL_SCRIPT = PROJECT_ROOT / "install" / "install.sh"
PROFILES = ("authoritative", "proxy-forwarder", "proxy-hybrid")


def _fake_bind_path(tmp_path: Path) -> Path:
    bindir = tmp_path / "fake-bin"
    bindir.mkdir(parents=True)
    for command in ("named", "named-checkconf", "named-checkzone", "rndc"):
        executable = bindir / command
        executable.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
        executable.chmod(0o755)
    python = bindir / "python3"
    python.symlink_to(Path(sys.executable))
    return bindir


def _run_install(tmp_path: Path, profile: str, *extra_args: str) -> tuple[Path, Path, Path]:
    bindir = _fake_bind_path(tmp_path)
    install_root = tmp_path / "opt" / "dnsforge"
    config_root = tmp_path / "etc" / "dnsforge"
    bin_link = tmp_path / "bin" / "dnsforge"
    bin_link.parent.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["PATH"] = f"{bindir}:{env['PATH']}"

    subprocess.run(
        [
            "bash",
            str(INSTALL_SCRIPT),
            "--profile",
            profile,
            "--install-root",
            str(install_root),
            "--config-root",
            str(config_root),
            "--bin-link",
            str(bin_link),
            *extra_args,
        ],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    return install_root, config_root, bin_link


@pytest.mark.skipif(os.geteuid() != 0, reason="install scripts intentionally require root")
@pytest.mark.parametrize("profile", PROFILES)
def test_install_script_deploys_profile_setup_conf(tmp_path: Path, profile: str) -> None:
    install_root, config_root, bin_link = _run_install(tmp_path, profile)

    actual = (config_root / "setup.conf").read_text(encoding="utf-8")

    assert 'ROLE="dns-' in actual
    assert "BIND_ADMIN_NICNAME" in actual
    assert not any(line.startswith("FRONT_IP=") for line in actual.splitlines())
    assert not any(line.startswith("BACK_IP=") for line in actual.splitlines())
    assert not any(line.startswith("ADM_IP=") for line in actual.splitlines())
    assert (install_root / "settings").is_symlink()
    assert (install_root / "settings").resolve() == config_root
    assert bin_link.is_symlink()
    assert bin_link.resolve() == install_root / "bin" / "dnsforge-system"


@pytest.mark.skipif(os.geteuid() != 0, reason="install scripts intentionally require root")
def test_install_script_keeps_existing_setup_conf_without_force(tmp_path: Path) -> None:
    _, config_root, _ = _run_install(tmp_path, "authoritative")
    setup_file = config_root / "setup.conf"
    setup_file.write_text('ROLE="custom"\n', encoding="utf-8")

    _run_install(tmp_path / "second", "proxy-hybrid", "--config-root", str(config_root))

    assert setup_file.read_text(encoding="utf-8") == 'ROLE="custom"\n'


@pytest.mark.skipif(os.geteuid() != 0, reason="install scripts intentionally require root")
def test_install_script_replaces_setup_conf_with_force(tmp_path: Path) -> None:
    _, config_root, _ = _run_install(tmp_path, "authoritative")
    setup_file = config_root / "setup.conf"
    setup_file.write_text('ROLE="custom"\n', encoding="utf-8")

    _run_install(
        tmp_path / "second",
        "proxy-forwarder",
        "--config-root",
        str(config_root),
        "--force",
    )

    actual = setup_file.read_text(encoding="utf-8")
    assert 'ROLE="dns-proxy"' in actual
    assert 'PROXY_TYPE="forwarder"' in actual
    assert "BIND_ADMIN_NICNAME" in actual
    assert not any(line.startswith("FRONT_IP=") for line in actual.splitlines())


def test_install_profile_templates_are_owned_by_project_resources() -> None:
    assert not (PROJECT_ROOT / "install" / "templates").exists()
    legacy_node_settings_scripts = list((PROJECT_ROOT / "install").glob("*node-settings*.sh"))
    assert legacy_node_settings_scripts == []
    generator = PROJECT_ROOT / "src" / "dnsforge" / "infrastructure" / "profile" / "setup_profile_generator.py"
    assert generator.is_file()
