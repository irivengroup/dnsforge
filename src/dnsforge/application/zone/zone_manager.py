from __future__ import annotations

from dnsforge.application.history.history_service import ZoneHistoryService
from dnsforge.domain.zone.model import ZoneDefinition, ZoneType
from dnsforge.domain.zone.record import DnsRecordExpressionParser
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.infrastructure.history.filesystem_repository import FilesystemHistoryRepository
from dnsforge.shared.errors import ZoneError


class ZoneManager:
    def __init__(self, paths: ProjectPaths, catalog: ZoneCatalog | None = None) -> None:
        self.paths = paths
        self.catalog = catalog or ZoneCatalog(paths.catalog_file)
        self.parser = DnsRecordExpressionParser()
        self.history = ZoneHistoryService(
            self.catalog,
            FilesystemHistoryRepository(),
        )

    def list(self):
        return self.catalog.list()

    def get(self, name: str):
        return self.catalog.get(name)

    def show(self, name: str) -> str:
        zone = self.get(name)
        lines = [
            f"Zone: {zone.name}",
            f"Type: {zone.zone_type.value}",
            f"Status: {'enabled' if zone.enabled else 'disabled'}",
            f"Views: {', '.join(zone.views)}",
            "",
            "Records:",
        ]
        if not zone.records:
            lines.append("  none")
        else:
            lines.extend(f"  {record.to_bind_line()}" for record in zone.records)
        return "\n".join(lines)

    def create(self, name, zone_type, views, cluster=None, enabled=True):
        self.catalog.create(ZoneDefinition(name, ZoneType.from_value(zone_type), views, cluster, enabled)); self.history.snapshot_current(name, 'create')
        self.history.snapshot_current(name, "create")

    def disable(self, name):
        self.catalog.disable(name)
        self.history.snapshot_current(name, "disable")

    def enable(self, name):
        self.catalog.enable(name)
        self.history.snapshot_current(name, "enable")

    def delete(self, name):
        self.history.snapshot_current(name, "pre-delete")
        self.catalog.delete(name)

    def add_record(self, zone_name, expr, ttl=None):
        zone = self.get(zone_name)
        record = self.parser.parse_add(expr, ttl)
        if record in zone.records:
            raise ZoneError("record already exists")
        self._save(zone, [*zone.records, record])
        self.history.snapshot_current(zone_name, "add-record")

    def update_record(self, zone_name, expr, ttl=None):
        zone = self.get(zone_name)
        new_record, old_value = self.parser.parse_update(expr, ttl)
        found = False
        records = []
        for record in zone.records:
            if (
                record.record_type == new_record.record_type
                and record.name == new_record.name
                and record.priority == new_record.priority
                and record.value == old_value
            ):
                records.append(new_record)
                found = True
            else:
                records.append(record)
        if not found:
            raise ZoneError("record to update not found")
        self._save(zone, records)
        self.history.snapshot_current(zone_name, "update-record")

    def delete_record(self, zone_name, expr):
        zone = self.get(zone_name)
        record_type, name, priority, value = self.parser.parse_delete(expr)
        found = False
        records = []
        for record in zone.records:
            match = (
                record.record_type == record_type
                and record.name == name
                and (priority is None or record.priority == priority)
                and (value is None or record.value == value)
            )
            if match:
                found = True
            else:
                records.append(record)
        if not found:
            raise ZoneError("record to delete not found")
        self._save(zone, records)
        self.history.snapshot_current(zone_name, "delete-record")

    def _save(self, zone, records):
        self.catalog.update(
            ZoneDefinition(
                zone.name,
                zone.zone_type,
                zone.views,
                zone.cluster,
                zone.enabled,
                zone.acl,
                records,
            )
        )

    def history_list(self, zone_name: str) -> str:
        return self.history.history(zone_name)

    def history_diff(self, zone_name: str, from_version: int, to_version: int) -> str:
        return self.history.diff(zone_name, from_version, to_version)

    def rollback(self, zone_name: str, version: int) -> str:
        return self.history.rollback(zone_name, version)

    def show_version(self, zone_name: str, version: int) -> str:
        return self.history.show_version(zone_name, version)
