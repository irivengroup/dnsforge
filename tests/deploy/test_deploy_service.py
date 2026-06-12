from __future__ import annotations

from pathlib import Path

from dnsforge.application.deploy.deploy_service import DeployService
from dnsforge.infrastructure.bind.layout import BindLayoutDetector
from dnsforge.infrastructure.initialize.state_store import InitializeStateStore


def test_deploy_service_applies_rendered_tree_without_initialization_lock(tmp_path: Path) -> None:
    render_root = tmp_path / "render"
    target_root = tmp_path / "target"
    setup_file = target_root / "etc/dnsforge/setup.conf"
    layout = BindLayoutDetector().from_family("redhat")

    (render_root / "etc/named").mkdir(parents=True)
    (render_root / "etc/named.conf").write_text("// DNSForge rendered named.conf\n", encoding="utf-8")

    DeployService(layout=layout).deploy(render_root, target_root=target_root, dry_run=True)

    assert InitializeStateStore().is_initialized(setup_file) is False


def test_deploy_service_requires_render_root_even_in_dry_run(tmp_path: Path) -> None:
    missing = tmp_path / "missing-render"
    layout = BindLayoutDetector().from_family("redhat")
    try:
        DeployService(layout=layout).deploy(missing, target_root=tmp_path / "target", dry_run=True)
    except FileNotFoundError as exc:
        assert "render root not found" in str(exc)
    else:
        raise AssertionError("deploy accepted a missing render root")
