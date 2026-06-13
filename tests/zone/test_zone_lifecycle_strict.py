from __future__ import annotations

import pytest
from pathlib import Path

from dnsforge.application.zone.zone_manager import ZoneManager
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.shared.errors import ZoneError


def manager(tmp_path: Path) -> ZoneManager:
    return ZoneManager(ProjectPaths(tmp_path), ZoneCatalog(tmp_path / "zones.yml"))


def test_zone_create_defaults_to_draft_and_enabled_inventory_means_active(tmp_path: Path) -> None:
    m = manager(tmp_path)
    m.create("example.com", "master", ["internal"], reason="unit test change")

    zone = m.get("example.com")
    assert zone.lifecycle.value == "draft"
    assert zone.enabled is True
    assert [z.name for z in m.list(enabled_only=True)] == []


def test_strict_lifecycle_transitions_are_enforced(tmp_path: Path) -> None:
    m = manager(tmp_path)
    m.create("example.com", "master", ["internal"], reason="unit test change")

    with pytest.raises(ZoneError, match="requires lifecycle retired"):
        m.delete("example.com", reason="unit test change")
    with pytest.raises(ZoneError, match="only active zones"):
        m.disable("example.com", reason="unit test change")

    m.enable("example.com", reason="unit test change")
    with pytest.raises(ZoneError, match="only draft zones"):
        m.enable("example.com", reason="unit test change")

    m.disable("example.com", reason="unit test change")
    with pytest.raises(ZoneError, match="requires lifecycle retired"):
        m.delete("example.com", reason="unit test change")

    m.retire("example.com", reason="unit test change")
    m.delete("example.com", reason="unit test change")
    assert m.list() == []


def test_zone_audit_reports_missing_governance_metadata(tmp_path: Path) -> None:
    m = manager(tmp_path)
    m.create("example.com", "master", ["internal"], reason="unit test change")

    ok, output = m.audit_zones()

    assert not ok
    assert "missing business owner" in output
    assert "missing technical owner" in output
    assert "missing classification" in output
