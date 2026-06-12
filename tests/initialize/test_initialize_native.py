from __future__ import annotations

import re
from pathlib import Path

from dnsforge.application.initialize.initialize_planner import InitializePlanner
from dnsforge.application.initialize.initialize_service import InitializeService
from dnsforge.infrastructure.install.file_installer import FileInstaller

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_initialize_application_does_not_call_legacy_bash() -> None:
    pattern = re.compile(r"LegacyShellRunner|dnsProxyDeploy\.sh|dnsAuthoritativeDeploy\.sh")
    offenders = []
    for path in (PROJECT_ROOT / "src/dnsforge/application/initialize").rglob("*.py"):
        if pattern.search(path.read_text(encoding="utf-8")):
            offenders.append(str(path.relative_to(PROJECT_ROOT)))
    assert offenders == []


def test_native_initialize_plan_can_apply_dry_run(tmp_path: Path) -> None:
    render = tmp_path / "render"
    target = tmp_path / "target"
    (render / "etc/named").mkdir(parents=True)
    (render / "etc/named.conf").write_text("// named\n", encoding="utf-8")

    mappings = FileInstaller().install_tree(render, target_root=target, dry_run=True)
    assert mappings

    plan = InitializePlanner().build_proxy_plan("proxy01", "forwarder", render, dry_run=True, backup_before_apply=True)
    setup_file = tmp_path / "etc/dnsforge/setup.conf"
    InitializeService().apply(plan, setup_file=setup_file)
    assert "Initialize plan" in plan.summary()
