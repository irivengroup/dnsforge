from __future__ import annotations

from pathlib import Path

from dnsforge.application.initialize.initialize_planner import InitializePlanner
from dnsforge.application.initialize.initialize_service import InitializeService


class _Backup:
    def __init__(self) -> None:
        self.called = False

    def create(self, *args, **kwargs):
        self.called = True
        raise AssertionError("backup should not run when backup_before_apply is false")


class _Deploy:
    def __init__(self) -> None:
        self.called = False

    def deploy(self, *args, **kwargs) -> None:
        self.called = True


class _StateStore:
    def __init__(self) -> None:
        self.marked = False

    def assert_not_initialized(self, setup_file: Path) -> None:
        return None

    def mark_initialized(self, setup_file: Path, role: str, node: str) -> None:
        self.marked = True


def test_initialize_does_not_install_packages(tmp_path: Path) -> None:
    render = tmp_path / "render"
    (render / "etc/named").mkdir(parents=True)
    (render / "etc/named.conf").write_text("// named\n", encoding="utf-8")
    setup_file = tmp_path / "etc/dnsforge/setup.conf"

    deploy = _Deploy()
    state = _StateStore()
    service = InitializeService(bind_backup=_Backup(), deploy_service=deploy, state_store=state)
    plan = InitializePlanner().build_authoritative_plan("auth01", render, dry_run=False, backup_before_apply=False)

    service.apply(plan, setup_file=setup_file)

    assert deploy.called is True
    assert state.marked is True
