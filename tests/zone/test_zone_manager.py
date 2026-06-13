from __future__ import annotations

from pathlib import Path

from dnsforge.domain.zone.model import ZoneDefinition, ZoneType
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.interfaces.cli.main import build_parser


def test_zone_cli_commands_parse() -> None:
    parser = build_parser()
    for command in (
        ["zone", "list"],
        ["zone", "get", "--name", "example.com"],
        [
            "zone",
            "create",
            "--name",
            "example.com",
            "--type",
            "master",
            "--views",
            "external,internal",
            "--reason",
            "unit test change",
        ],
        ["zone", "disable", "--name", "example.com", "--reason", "unit test change"],
        ["zone", "enable", "--name", "example.com", "--reason", "unit test change"],
        ["zone", "retire", "--name", "example.com", "--reason", "unit test change"],
        ["zone", "delete", "--name", "example.com", "--reason", "unit test change"],
    ):
        parser.parse_args(command)


def test_zone_catalog_lifecycle(tmp_path: Path) -> None:
    catalog = ZoneCatalog(tmp_path / "zones.yml")
    zone = ZoneDefinition(
        name="example.test",
        zone_type=ZoneType.MASTER,
        views=["external", "internal"],
        cluster="A",
    )
    catalog.create(zone)
    assert [item.name for item in catalog.list()] == ["example.test"]
    assert catalog.get("example.test").zone_type.value == "master"
    catalog.disable("example.test")
    assert catalog.get("example.test").enabled is False
    catalog.enable("example.test")
    assert catalog.get("example.test").enabled is True
    catalog.delete("example.test")
    assert len(catalog.list()) == 0
