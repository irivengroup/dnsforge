from __future__ import annotations

from pathlib import Path

import pytest

from dnsforge.application.zone.zone_manager import ZoneManager
from dnsforge.domain.zone.model import ZoneDefinition, ZoneType
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class FailingOnceZoneCatalog(ZoneCatalog):
    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self.fail_next_save = False

    def save(self, zones: list[ZoneDefinition]) -> None:
        if self.fail_next_save:
            self.fail_next_save = False
            raise RuntimeError("simulated catalog persistence failure")
        super().save(zones)


def test_zone_record_change_is_atomic_when_catalog_commit_fails(tmp_path: Path) -> None:
    catalog = FailingOnceZoneCatalog(tmp_path / "zones.yml")
    manager = ZoneManager(ProjectPaths(tmp_path), catalog=catalog)
    manager.create("example.com", "master", ["internal"])

    catalog.fail_next_save = True
    with pytest.raises(RuntimeError, match="simulated catalog persistence failure"):
        manager.add_record("example.com", "A:www:192.168.100.10")

    zone = manager.get("example.com")
    assert zone.records == []
    assert [item.name for item in manager.list()] == ["example.com"]
    assert not (tmp_path / "backups" / "history" / "100.168.192.in-addr.arpa").exists()


def test_zone_record_update_commits_forward_and_reverse_together(tmp_path: Path) -> None:
    catalog = ZoneCatalog(tmp_path / "zones.yml")
    manager = ZoneManager(ProjectPaths(tmp_path), catalog=catalog)
    manager.create("example.com", "master", ["internal"])

    manager.add_record("example.com", "A:app:192.168.100.10")
    manager.update_record("example.com", "A:app:192.168.100.10:192.168.101.20")

    assert "192.168.101.20" in manager.show("example.com")
    assert "100.168.192.in-addr.arpa" not in [item.name for item in manager.list()]
    assert "20 IN PTR app.example.com." in manager.show("101.168.192.in-addr.arpa")
