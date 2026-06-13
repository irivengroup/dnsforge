from __future__ import annotations

from pathlib import Path

from dnsforge.application.zone.zone_manager import ZoneManager
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


def manager(tmp_path: Path) -> ZoneManager:
    paths = ProjectPaths(tmp_path)
    return ZoneManager(paths, ZoneCatalog(tmp_path / "zones.yml"))


def test_forward_a_record_creates_managed_reverse_zone(tmp_path: Path) -> None:
    m = manager(tmp_path)
    m.create("example.com", "master", ["external"], reason="unit test change")
    m.add_record("example.com", "A:www:192.168.100.10", ttl=300, reason="unit test change")

    reverse = m.get("100.168.192.in-addr.arpa")
    assert reverse.managed_reverse is True
    assert reverse.zone_type.value == "reverse-master"
    assert reverse.views == ["external"]
    assert [r.to_bind_line() for r in reverse.records] == ["10 300 IN PTR www.example.com."]


def test_forward_a_record_update_updates_reverse_zone(tmp_path: Path) -> None:
    m = manager(tmp_path)
    m.create("example.com", "master", ["internal"], reason="unit test change")
    m.add_record("example.com", "A:app:192.168.100.10", reason="unit test change")
    m.update_record("example.com", "A:app:192.168.100.10:192.168.101.20", reason="unit test change")

    assert "100.168.192.in-addr.arpa" not in [z.name for z in m.list()]
    reverse = m.get("101.168.192.in-addr.arpa")
    assert [r.to_bind_line() for r in reverse.records] == ["20 IN PTR app.example.com."]


def test_forward_a_record_delete_removes_empty_managed_reverse_zone(tmp_path: Path) -> None:
    m = manager(tmp_path)
    m.create("example.com", "master", ["external", "internal"], reason="unit test change")
    m.add_record("example.com", "A:www:192.168.100.10", reason="unit test change")
    m.delete_record("example.com", "A:www:192.168.100.10", reason="unit test change")

    assert "100.168.192.in-addr.arpa" not in [z.name for z in m.list()]


def test_delete_forward_zone_removes_its_reverse_records(tmp_path: Path) -> None:
    m = manager(tmp_path)
    m.create("example.com", "master", ["external"], lifecycle="active", reason="unit test change")
    m.add_record("example.com", "A:www:192.168.100.10", reason="unit test change")
    m.disable("example.com", reason="unit test change")
    m.retire("example.com", reason="unit test change")
    m.delete("example.com", reason="unit test change")

    assert m.list() == []
