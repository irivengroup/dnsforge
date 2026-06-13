from __future__ import annotations

from pathlib import Path

from dnsforge.application.zone.zone_manager import ZoneManager
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


def test_zone_catalog_governance_metadata_is_persisted_and_searchable(tmp_path: Path) -> None:
    manager = ZoneManager(ProjectPaths(tmp_path), ZoneCatalog(tmp_path / "zones.yml"))
    manager.create(
        "finance.example.com",
        "master",
        ["internal"],
        description="Finance internal DNS",
        business_owner="Finance",
        technical_owner="DNS Team",
        environment="production",
        classification="internal",
        lifecycle="active",
        reason="unit test change",
    )

    zone = manager.get("finance.example.com")
    assert zone.business_owner == "Finance"
    assert zone.technical_owner == "DNS Team"
    assert zone.environment == "production"
    assert zone.classification == "internal"
    assert "Business Owner: Finance" in manager.show("finance.example.com")

    assert [z.name for z in manager.search_zones(owner="Finance")] == ["finance.example.com"]
    assert [z.name for z in manager.search_zones(environment="production")] == ["finance.example.com"]


def test_zone_record_search_inside_zone(tmp_path: Path) -> None:
    manager = ZoneManager(ProjectPaths(tmp_path), ZoneCatalog(tmp_path / "zones.yml"))
    manager.create("example.com", "master", ["internal"], lifecycle="active", reason="unit test change")
    manager.add_record("example.com", "A:www:192.168.10.10", reason="unit test change")
    manager.add_record("example.com", "CNAME:app:www.example.com.", reason="unit test change")

    assert [record.name for record in manager.search_records("example.com", record_name="www")] == ["www"]
    assert [record.name for record in manager.search_records("example.com", record_type="CNAME")] == ["app"]
    assert [record.name for record in manager.search_records("example.com", value="192.168")] == ["www"]
