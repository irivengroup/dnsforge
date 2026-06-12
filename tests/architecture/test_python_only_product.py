from __future__ import annotations

import re
import tempfile
from pathlib import Path

from dnsforge.application.initialize.initialize_planner import InitializePlanner
from dnsforge.application.initialize.initialize_service import InitializeService
from dnsforge.infrastructure.install.file_installer import FileInstaller
from dnsforge.interfaces.cli.main import build_parser

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_python_project_entrypoints_exist() -> None:
    assert (PROJECT_ROOT / "pyproject.toml").is_file()
    assert (PROJECT_ROOT / "bin/dnsforge").is_file()


def test_product_code_does_not_reference_legacy_shell_entrypoints() -> None:
    pattern = re.compile(r"LegacyShellRunner|dnsProxyDeploy\.sh|dnsAuthoritativeDeploy\.sh|zone-manager\.sh")
    offenders = []
    for path in (PROJECT_ROOT / "src/dnsforge").rglob("*.py"):
        if pattern.search(path.read_text(encoding="utf-8")):
            offenders.append(str(path.relative_to(PROJECT_ROOT)))
    assert offenders == []


def test_cli_and_initialize_flow_are_python_native() -> None:
    parser = build_parser()
    parser.parse_args(["validate", "proxy", "proxy01", "--type", "forwarder"])
    parser.parse_args(["render", "proxy", "proxy01", "--type", "hybrid"])
    parser.parse_args(["initialize", "proxy", "proxy01", "--type", "forwarder", "--dry-run"])
    parser.parse_args(["zone", "list"])

    with tempfile.TemporaryDirectory() as tmp:
        render = Path(tmp) / "render"
        (render / "etc/named").mkdir(parents=True)
        (render / "etc/named.conf").write_text("// named\n", encoding="utf-8")
        assert FileInstaller().install_tree(render, target_root=Path(tmp) / "target", dry_run=True)
        plan = InitializePlanner().build_proxy_plan("proxy01", "forwarder", render, dry_run=True, backup_before_apply=True)
        setup_file = Path(tmp) / "etc/dnsforge/setup.conf"
        InitializeService().apply(plan, setup_file=setup_file)
