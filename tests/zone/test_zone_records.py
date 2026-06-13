from __future__ import annotations

from pathlib import Path

from dnsforge.application.zone.zone_manager import ZoneManager
from dnsforge.domain.zone.model import ZoneDefinition, ZoneType
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.interfaces.cli.main import build_parser


def test_zone_record_cli_commands_parse() -> None:
    parser = build_parser()
    parser.parse_args(["zone", "show", "example.com"])
    parser.parse_args(["zone", "edit", "example.com", "--add", "A:www:192.168.10.10", "--reason", "unit test change"])
    parser.parse_args(
        ["zone", "edit", "example.com", "--update", "A:www:192.168.10.10:192.168.10.15", "--reason", "unit test change"]
    )
    parser.parse_args(["zone", "edit", "example.com", "--delete", "A:www", "--reason", "unit test change"])


def test_zone_record_lifecycle(tmp_path: Path) -> None:
    catalog = ZoneCatalog(tmp_path / "zones.yml")
    manager = ZoneManager(ProjectPaths(tmp_path), catalog=catalog)
    catalog.create(ZoneDefinition("example.com", ZoneType.MASTER, ["external"]))
    manager.add_record("example.com", "A:www:192.168.10.10", ttl=300, reason="unit test change")
    assert "www 300 IN A 192.168.10.10" in manager.show("example.com")
    manager.update_record("example.com", "A:www:192.168.10.10:192.168.10.15", ttl=300, reason="unit test change")
    assert "192.168.10.15" in manager.show("example.com")
    manager.delete_record("example.com", "A:www", reason="unit test change")
    assert "none" in manager.show("example.com")
