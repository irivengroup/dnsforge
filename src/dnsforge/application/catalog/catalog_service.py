from __future__ import annotations

from dataclasses import replace
import os
from pathlib import Path

from dnsforge.application.zone.zone_manager import require_reason
from dnsforge.domain.catalog.model import CatalogState, CatalogStateDocument, CatalogZoneEntry
from dnsforge.domain.zone.model import ZoneLifecycleState, ZoneType
from dnsforge.infrastructure.bind.rendering.template_service import TemplateService
from dnsforge.infrastructure.catalog.catalog_state_repository import CatalogStateRepository
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.shared.errors import DnsForgeError


class CatalogService:
    def __init__(
        self,
        paths: ProjectPaths,
        state_repository: CatalogStateRepository | None = None,
        zone_catalog: ZoneCatalog | None = None,
        template_service: TemplateService | None = None,
    ) -> None:
        self.paths = paths
        self.repository = state_repository or CatalogStateRepository(paths.settings_root / "catalog-state.yml")
        self.zone_catalog = zone_catalog or ZoneCatalog(paths.catalog_file)
        self.template_service = template_service or TemplateService(layout=paths.bind_layout)

    def status(self) -> str:
        document = self.repository.load()
        entries = document.active_entries()
        return "\n".join(
            [
                f"Catalog: {document.state.value}",
                f"Published Zones: {len(entries)}",
                f"Last Reason: {document.last_reason or 'unset'}",
            ]
        )

    def enable(self, reason: str) -> str:
        normalized = require_reason(reason)
        document = self.repository.load()
        updated = replace(document, state=CatalogState.ENABLED, last_reason=normalized)
        self.repository.save(updated)
        return "Catalog zones enabled"

    def disable(self, reason: str) -> str:
        normalized = require_reason(reason)
        document = self.repository.load()
        updated = replace(document, state=CatalogState.DISABLED, last_reason=normalized, entries=[])
        self.repository.save(updated)
        return "Catalog zones disabled"

    def sync(self, reason: str) -> str:
        normalized = require_reason(reason)
        document = self.repository.load()
        if document.state is not CatalogState.ENABLED:
            raise DnsForgeError("catalog zones must be enabled before sync")
        entries = self._published_entries()
        updated = replace(document, last_reason=normalized, entries=entries)
        self.repository.save(updated)
        self._write_catalog_zone(entries)
        return f"Catalog synchronized: {len(entries)} zones published"

    def list_published(self) -> str:
        document = self.repository.load()
        entries = document.active_entries()
        if not entries:
            return "No catalog zones published"
        lines = ["Zone\tType\tViews\tMember"]
        lines.extend(
            f"{entry.zone_name}\t{entry.zone_type}\t{','.join(entry.views)}\t{entry.member_name}" for entry in entries
        )
        return "\n".join(lines)

    def validate(self) -> str:
        document = self.repository.load()
        findings: list[str] = []
        if document.state is CatalogState.ENABLED:
            missing, stale = self._diff(document)
            findings.extend(f"missing catalog publication: {zone}" for zone in missing)
            findings.extend(f"stale catalog publication: {zone}" for zone in stale)
        if findings:
            raise DnsForgeError("\n".join(findings))
        return "Catalog validation OK"

    def repair(self, reason: str) -> str:
        normalized = require_reason(reason)
        document = self.repository.load()
        if document.state is not CatalogState.ENABLED:
            raise DnsForgeError("catalog zones must be enabled before repair")
        missing, stale = self._diff(document)
        entries = self._published_entries()
        updated = replace(document, last_reason=normalized, entries=entries)
        self.repository.save(updated)
        self._write_catalog_zone(entries)
        return f"Catalog repaired: {len(missing)} missing added, {len(stale)} stale removed"

    def audit(self) -> tuple[bool, str]:
        document = self.repository.load()
        expected = self._published_entries()
        if document.state is CatalogState.DISABLED:
            return False, "Catalog zones disabled"
        if not expected:
            return False, "Catalog enabled but no active zones are eligible for publication"
        missing, stale = self._diff(document)
        if missing:
            return False, "Missing catalog publications:\n" + "\n".join(f"- {zone}" for zone in missing)
        if stale:
            return False, "Stale catalog publications:\n" + "\n".join(f"- {zone}" for zone in stale)
        return True, "Catalog audit OK"

    def _diff(self, document: CatalogStateDocument) -> tuple[list[str], list[str]]:
        published = {entry.zone_name for entry in document.active_entries()}
        expected = {entry.zone_name for entry in self._published_entries()}
        return sorted(expected - published), sorted(published - expected)

    def _published_entries(self) -> list[CatalogZoneEntry]:
        entries: list[CatalogZoneEntry] = []
        for zone in self.zone_catalog.list():
            if not zone.enabled or zone.lifecycle is not ZoneLifecycleState.ACTIVE:
                continue
            if zone.zone_type in {ZoneType.FORWARD, ZoneType.HINT, ZoneType.RPZ, ZoneType.CATALOG}:
                continue
            entries.append(
                CatalogZoneEntry(
                    zone.name,
                    zone.zone_type.value,
                    list(zone.views),
                    self._member_name(zone.name),
                )
            )
        return entries

    def _member_name(self, zone_name: str) -> str:
        safe = zone_name.rstrip(".").replace(".", "-")
        return f"{safe}.zones"

    def _write_catalog_zone(self, entries: list[CatalogZoneEntry]) -> None:
        rendered = self._render_catalog_zone(entries)
        path = self.paths.bind_layout.catalog_zone_file
        target_root = os.environ.get("DNSFORGE_BIND_TARGET_ROOT", "").strip()
        if target_root and path.is_absolute():
            path = Path(target_root) / path.relative_to("/")
        elif not path.is_absolute():
            path = self.paths.project_root / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")

    def _render_catalog_zone(self, entries: list[CatalogZoneEntry]) -> str:
        member_lines = []
        for index, entry in enumerate(entries, start=1):
            member_lines.append(f'{entry.member_name} 300 IN PTR "{entry.zone_name}"')
            member_lines.append(f'{index}.group.zones 300 IN TXT "{entry.zone_name}"')
        variables = {
            "CATALOG_SERIAL": "1",
            "CATALOG_MEMBERS": "\n".join(member_lines) if member_lines else "; no active catalog members",
        }
        return self.template_service.render_file("catalog.zone.j2", variables)
