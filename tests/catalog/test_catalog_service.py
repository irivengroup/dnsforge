from __future__ import annotations

from pathlib import Path

import pytest

from dnsforge.application.catalog.catalog_service import CatalogService
from dnsforge.application.zone.zone_manager import ZoneManager
from dnsforge.infrastructure.catalog.catalog_state_repository import CatalogStateRepository
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.shared.errors import DnsForgeError


def _manager(tmp_path: Path) -> ZoneManager:
    return ZoneManager(ProjectPaths(tmp_path), ZoneCatalog(tmp_path / "zones.yml"))


def _service(tmp_path: Path) -> CatalogService:
    return CatalogService(
        ProjectPaths(tmp_path),
        CatalogStateRepository(tmp_path / "catalog-state.yml"),
        ZoneCatalog(tmp_path / "zones.yml"),
    )


def test_catalog_lifecycle_publishes_active_authoritative_zones(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DNSFORGE_BIND_TARGET_ROOT", str(tmp_path / "target"))
    manager = _manager(tmp_path)
    manager.create("example.com", "master", ["external"], lifecycle="active", reason="catalog unit test")
    manager.create("draft.example", "master", ["internal"], lifecycle="draft", reason="catalog unit test")
    manager.create("forward.example", "forward", ["internal"], lifecycle="active", reason="catalog unit test")

    service = _service(tmp_path)
    assert "enabled" in service.enable("catalog enable test")
    assert "1 zones published" in service.sync("catalog sync test")
    assert "example.com" in service.list_published()
    assert "draft.example" not in service.list_published()
    assert "Catalog validation OK" == service.validate()

    rendered = tmp_path / "target" / ProjectPaths(tmp_path).bind_layout.catalog_zone_file.relative_to("/")
    assert rendered.exists()
    text = rendered.read_text(encoding="utf-8")
    assert '"example.com"' in text
    assert "forward.example" not in text


def test_catalog_sync_requires_enabled_state(tmp_path: Path) -> None:
    manager = _manager(tmp_path)
    manager.create("example.com", "master", ["external"], lifecycle="active", reason="catalog unit test")

    with pytest.raises(DnsForgeError):
        _service(tmp_path).sync("catalog sync test")


def test_catalog_mutations_require_reason(tmp_path: Path) -> None:
    with pytest.raises(DnsForgeError):
        _service(tmp_path).enable("short")
