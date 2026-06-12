from __future__ import annotations

from dnsforge.domain.zone.model import ZoneDefinition
from dnsforge.domain.zone.record import DnsRecord
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.infrastructure.history.filesystem_repository import FilesystemHistoryRepository


class ZoneHistoryService:
    def __init__(self, catalog: ZoneCatalog, repository: FilesystemHistoryRepository | None = None) -> None:
        self.catalog = catalog
        self.repository = repository or FilesystemHistoryRepository()

    def snapshot_current(self, zone_name: str, action: str) -> None:
        try:
            zone = self.catalog.get(zone_name)
        except Exception:
            return
        self.repository.create_snapshot(zone_name, self._zone_to_content(zone), action=action)

    def current_version(self, zone_name: str) -> int:
        return self.repository.current_version(zone_name)

    def history(self, zone_name: str) -> str:
        snapshots = self.repository.list(zone_name)
        current = self.current_version(zone_name)
        lines = [f"Zone: {zone_name}", f"Current Version: {current}", "", "Version\tTimestamp\tAction"]
        if snapshots:
            lines.extend(snapshot.title() for snapshot in snapshots)
        else:
            lines.append("none")
        return "\n".join(lines)

    def show_version(self, zone_name: str, version: int) -> str:
        return self.repository.get(zone_name, version).content

    def diff(self, zone_name: str, from_version: int, to_version: int) -> str:
        return self.repository.diff(zone_name, from_version, to_version)

    def rollback(self, zone_name: str, version: int) -> str:
        snapshot = self.repository.get(zone_name, version)
        current = self.catalog.get(zone_name)
        self.snapshot_current(zone_name, f"pre-rollback-to-{version}")
        restored = self._content_to_zone(snapshot.content, current)
        self.catalog.update(restored)
        self.snapshot_current(zone_name, f"rollback-to-{version}")
        new_version = self.current_version(zone_name)
        return f"Rollback completed: {zone_name} -> version {version}; current version {new_version}"

    def _zone_to_content(self, zone: ZoneDefinition) -> str:
        lines = [
            f"name: {zone.name}",
            f"type: {zone.zone_type.value}",
            f"enabled: {'yes' if zone.enabled else 'no'}",
            "views:",
        ]
        lines.extend(f"  - {view}" for view in zone.views)
        lines.append("records:")
        for record in zone.records:
            lines.append(f"  - type: {record.record_type.value}")
            lines.append(f"    name: {record.name}")
            if record.ttl is not None:
                lines.append(f"    ttl: {record.ttl}")
            if record.priority is not None:
                lines.append(f"    priority: {record.priority}")
            lines.append(f"    value: {record.value}")
        return "\n".join(lines) + "\n"

    def _content_to_zone(self, content: str, fallback: ZoneDefinition) -> ZoneDefinition:
        from dnsforge.domain.zone.record import DnsRecord, DnsRecordType

        records: list[DnsRecord] = []
        current: dict[str, str] | None = None
        for raw in content.splitlines():
            stripped = raw.strip()
            if stripped.startswith("- type:"):
                if current:
                    records.append(self._record(current))
                current = {"type": stripped.split(":", 1)[1].strip()}
            elif current is not None and ":" in stripped:
                key, value = stripped.split(":", 1)
                current[key.strip()] = value.strip()
        if current:
            records.append(self._record(current))

        return ZoneDefinition(
            name=fallback.name,
            zone_type=fallback.zone_type,
            views=list(fallback.views),
            cluster=fallback.cluster,
            enabled=fallback.enabled,
            acl=dict(fallback.acl),
            records=records,
        )

    def _record(self, data: dict[str, str]) -> DnsRecord:
        from dnsforge.domain.zone.record import DnsRecord, DnsRecordType

        return DnsRecord(
            record_type=DnsRecordType.from_value(data["type"]),
            name=data.get("name", "@"),
            value=data.get("value", ""),
            ttl=int(data["ttl"]) if data.get("ttl") else None,
            priority=int(data["priority"]) if data.get("priority") else None,
        )
