from __future__ import annotations

from pathlib import Path

from dnsforge.application.zone.zone_manager import ZoneManager
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.interfaces.cli.application import DnsForgeArgumentParserFactory, DnsForgeCli
from dnsforge.infrastructure.system.privilege_guard import RootPrivilegeGuard


class NoopPrivilegeGuard(RootPrivilegeGuard):
    def require_root(self) -> None:
        return None


def test_requested_zone_lifecycle_commands_parse() -> None:
    parser = DnsForgeArgumentParserFactory().build()
    commands = [
        ["zone", "list"],
        ["zone", "list", "--enabled"],
        ["zone", "create", "example.com", "--reason", "unit test change"],
        [
            "zone",
            "create",
            "example.com",
            "--type",
            "master",
            "--views",
            "internal,external",
            "--reason",
            "unit test change",
        ],
        ["zone", "show", "example.com"],
        ["zone", "edit", "example.com", "--add", "A:www:192.168.10.10", "--reason", "unit test change"],
        ["zone", "disable", "example.com", "--reason", "unit test change"],
        ["zone", "enable", "example.com", "--reason", "unit test change"],
        ["zone", "status", "example.com"],
        ["zone", "backup", "example.com", "--reason", "unit test change"],
        ["zone", "retire", "example.com", "--reason", "unit test change"],
        ["zone", "delete", "example.com", "--reason", "unit test change"],
        ["zone", "history", "example.com"],
        ["zone", "diff", "--zone", "example.com", "--from", "1", "--to", "2"],
        ["zone", "rollback", "--zone", "example.com", "--version", "1", "--reason", "unit test change"],
        ["zone", "search", "--owner", "Finance"],
        ["zone", "search", "--zone", "example.com", "--record-name", "www"],
    ]
    for command in commands:
        parser.parse_args(command)


def test_zone_lifecycle_manager_operations(tmp_path: Path) -> None:
    manager = ZoneManager(ProjectPaths(tmp_path), ZoneCatalog(tmp_path / "zones.yml"))
    manager.create("example.com", "master", ["internal"], reason="unit test change")
    assert [zone.name for zone in manager.list()] == ["example.com"]
    assert [zone.name for zone in manager.list(enabled_only=True)] == []

    assert "Lifecycle: draft" in manager.status("example.com")
    manager.enable("example.com", reason="unit test change")
    assert [zone.name for zone in manager.list(enabled_only=True)] == ["example.com"]
    assert "Lifecycle: active" in manager.status("example.com")
    assert "Zone backup created: example.com#3" in manager.backup("example.com", reason="unit test change")

    manager.add_record("example.com", "A:www:192.168.10.10", reason="unit test change")
    assert "www IN A 192.168.10.10" in manager.show("example.com")
    assert "@current" in manager.diff_current("example.com", 1)
    assert "@1" in manager.history_diff("example.com", 1, 3)

    manager.disable("example.com", reason="unit test change")
    assert "example.com" not in [zone.name for zone in manager.list(enabled_only=True)]
    assert "Status: disabled" in manager.status("example.com")
    assert "Lifecycle: deprecated" in manager.status("example.com")

    manager.rollback("example.com", 1, reason="unit test change")
    assert "none" in manager.show("example.com")
    assert "example.com" in [zone.name for zone in manager.search_zones(view="internal")]

    manager.enable("example.com", reason="unit test change")
    manager.disable("example.com", reason="unit test change")
    manager.retire("example.com", reason="unit test change")
    assert "Lifecycle: retired" in manager.status("example.com")
    manager.delete("example.com", reason="unit test change")
    assert "example.com" not in [zone.name for zone in manager.list()]
