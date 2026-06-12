from __future__ import annotations

import ipaddress

from dnsforge.application.history.history_service import ZoneHistoryService
from dnsforge.domain.zone.model import ZoneDefinition, ZoneType
from dnsforge.domain.zone.record import DnsRecord, DnsRecordExpressionParser, DnsRecordType
from dnsforge.domain.zone.reverse import is_reverse_zone_name, reverse_mapping_for_address
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
            f"Managed Reverse: {'yes' if zone.managed_reverse else 'no'}",
            "",
            "Records:",
        ]
        if not zone.records:
            lines.append("  none")
        else:
            lines.extend(f"  {record.to_bind_line()}" for record in zone.records)
        return "\n".join(lines)

    def create(self, name, zone_type, views, cluster=None, enabled=True):
        self.catalog.create(ZoneDefinition(name, ZoneType.from_value(zone_type), views, cluster, enabled))
        self.history.snapshot_current(name, "create")

    def disable(self, name):
        self.catalog.disable(name)
        self.history.snapshot_current(name, "disable")

    def enable(self, name):
        self.catalog.enable(name)
        self.history.snapshot_current(name, "enable")

    def delete(self, name):
        zone = self.get(name)
        self.history.snapshot_current(name, "pre-delete")
        for record in zone.records:
            self._apply_reverse_delete(zone, record)
        self.catalog.delete(name)

    def add_record(self, zone_name, expr, ttl=None):
        zone = self.get(zone_name)
        record = self.parser.parse_add(expr, ttl)
        if record in zone.records:
            raise ZoneError("record already exists")
        self._save(zone, [*zone.records, record])
        self._apply_reverse_add(zone, record)
        self.history.snapshot_current(zone_name, "add-record")

    def update_record(self, zone_name, expr, ttl=None):
        zone = self.get(zone_name)
        new_record, old_value = self.parser.parse_update(expr, ttl)
        found = False
        records = []
        old_record: DnsRecord | None = None
        for record in zone.records:
            if (
                record.record_type == new_record.record_type
                and record.name == new_record.name
                and record.priority == new_record.priority
                and record.value == old_value
            ):
                records.append(new_record)
                old_record = record
                found = True
            else:
                records.append(record)
        if not found or old_record is None:
            raise ZoneError("record to update not found")
        self._save(zone, records)
        self._apply_reverse_delete(zone, old_record)
        self._apply_reverse_add(zone, new_record)
        self.history.snapshot_current(zone_name, "update-record")

    def delete_record(self, zone_name, expr):
        zone = self.get(zone_name)
        record_type, name, priority, value = self.parser.parse_delete(expr)
        found = False
        records = []
        removed: list[DnsRecord] = []
        for record in zone.records:
            match = (
                record.record_type == record_type
                and record.name == name
                and (priority is None or record.priority == priority)
                and (value is None or record.value == value)
            )
            if match:
                found = True
                removed.append(record)
            else:
                records.append(record)
        if not found:
            raise ZoneError("record to delete not found")
        self._save(zone, records)
        for record in removed:
            self._apply_reverse_delete(zone, record)
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
                zone.managed_reverse,
            )
        )

    def _apply_reverse_add(self, zone: ZoneDefinition, record: DnsRecord) -> None:
        mapping_record = self._reverse_record_for(zone, record)
        if mapping_record is None:
            return
        reverse_name, ptr_record = mapping_record
        reverse_zone = self._get_or_create_reverse_zone(reverse_name, zone)
        if ptr_record not in reverse_zone.records:
            self.catalog.update(self._replace_records(reverse_zone, [*reverse_zone.records, ptr_record]))
            self.history.snapshot_current(reverse_name, "sync-reverse-add")

    def _apply_reverse_delete(self, zone: ZoneDefinition, record: DnsRecord) -> None:
        mapping_record = self._reverse_record_for(zone, record)
        if mapping_record is None:
            return
        reverse_name, ptr_record = mapping_record
        try:
            reverse_zone = self.get(reverse_name)
        except ZoneError:
            return
        records = [item for item in reverse_zone.records if item != ptr_record]
        self.catalog.update(self._replace_records(reverse_zone, records))
        self.history.snapshot_current(reverse_name, "sync-reverse-delete")
        if reverse_zone.managed_reverse and not records:
            self.catalog.delete(reverse_name)

    def _reverse_record_for(self, zone: ZoneDefinition, record: DnsRecord) -> tuple[str, DnsRecord] | None:
        if zone.managed_reverse or is_reverse_zone_name(zone.name):
            return None
        if record.record_type not in {DnsRecordType.A, DnsRecordType.AAAA}:
            return None
        try:
            ipaddress.ip_address(record.value)
        except ValueError:
            return None
        target = self._absolute_owner(zone.name, record.name)
        mapping = reverse_mapping_for_address(record.value, target)
        return mapping.zone_name, DnsRecord(DnsRecordType.PTR, mapping.ptr_owner, mapping.ptr_target, ttl=record.ttl)

    def _get_or_create_reverse_zone(self, reverse_name: str, source_zone: ZoneDefinition) -> ZoneDefinition:
        try:
            return self.get(reverse_name)
        except ZoneError:
            reverse_zone = ZoneDefinition(
                name=reverse_name,
                zone_type=ZoneType.MASTER,
                views=list(source_zone.views),
                cluster=source_zone.cluster,
                enabled=source_zone.enabled,
                acl=dict(source_zone.acl),
                records=[],
                managed_reverse=True,
            )
            self.catalog.create(reverse_zone)
            self.history.snapshot_current(reverse_name, "create-managed-reverse")
            return reverse_zone

    def _replace_records(self, zone: ZoneDefinition, records: list[DnsRecord]) -> ZoneDefinition:
        return ZoneDefinition(
            zone.name,
            zone.zone_type,
            list(zone.views),
            zone.cluster,
            zone.enabled,
            dict(zone.acl),
            records,
            zone.managed_reverse,
        )

    def _absolute_owner(self, zone_name: str, record_name: str) -> str:
        if record_name == "@":
            return zone_name.rstrip(".") + "."
        if record_name.endswith("."):
            return record_name
        return f"{record_name}.{zone_name.rstrip('.')}."

    def history_list(self, zone_name: str) -> str:
        return self.history.history(zone_name)

    def history_diff(self, zone_name: str, from_version: int, to_version: int) -> str:
        return self.history.diff(zone_name, from_version, to_version)

    def rollback(self, zone_name: str, version: int) -> str:
        return self.history.rollback(zone_name, version)

    def show_version(self, zone_name: str, version: int) -> str:
        return self.history.show_version(zone_name, version)
