from __future__ import annotations

from pathlib import Path

from dnsforge.application.initialize.initialize_service import InitializeService
from dnsforge.application.initialize.initialize_planner import InitializePlanner


class _PackageManager:
    def __init__(self) -> None:
        self.called = False
        self.dry_run: bool | None = None

    def ensure_bind(self, dry_run: bool = False) -> list[list[str]]:
        self.called = True
        self.dry_run = dry_run
        return [["dnf", "install", "-y", "bind", "bind-utils"]]


def test_initialize_apply_bootstraps_bind_when_missing(tmp_path: Path) -> None:
    render = tmp_path / "render"
    (render / "etc/named").mkdir(parents=True)
    (render / "etc/named.conf").write_text("// named\n", encoding="utf-8")
    setup_file = tmp_path / "etc/dnsforge/setup.conf"

    package_manager = _PackageManager()
    service = InitializeService(package_manager=package_manager)
    plan = InitializePlanner().build_authoritative_plan("auth01", render, dry_run=True, backup_before_apply=False)

    service.apply(plan, setup_file=setup_file)

    assert package_manager.called is True
    assert package_manager.dry_run is True
