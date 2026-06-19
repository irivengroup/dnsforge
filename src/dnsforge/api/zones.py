from __future__ import annotations

from dnsforge.application.events.event_bus import EventBus
from dnsforge.application.zone.zone_manager import ZoneManager
from dnsforge.domain.events.model import AuditEvent
from dnsforge.infrastructure.audit.event_repository import AuditEventRepository
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class ZoneApi:
    def __init__(self, paths: ProjectPaths, event_bus: EventBus | None = None, audit: AuditEventRepository | None = None) -> None:
        self.paths = paths
        self.manager = ZoneManager(paths)
        self.event_bus = event_bus or EventBus()
        self.audit = audit

    def list_zones(self, enabled_only: bool = False):
        return self.manager.list(enabled_only=enabled_only)

    def search_zones(self, **criteria):
        return self.manager.search_zones(**criteria)

    def create_zone(self, name: str, zone_type: str, views: list[str], reason: str, **metadata) -> None:
        self.manager.create(name, zone_type, views, reason=reason, **metadata)
        self._publish("ZoneCreated", name, f"zone created: {name}", {"zone_type": zone_type, "views": views})

    def update_zone(self, name: str, record_expression: str, reason: str, ttl: int | None = None) -> None:
        self.manager.update_record(name, record_expression, ttl=ttl, reason=reason)
        self._publish("ZoneUpdated", name, f"zone updated: {name}")

    def delete_zone(self, name: str, reason: str) -> None:
        self.manager.delete(name, reason)
        self._publish("ZoneDeleted", name, f"zone deleted: {name}")

    def enable_zone(self, name: str, reason: str) -> None:
        self.manager.enable(name, reason)
        self._publish("ZoneEnabled", name, f"zone enabled: {name}")

    def disable_zone(self, name: str, reason: str) -> None:
        self.manager.disable(name, reason)
        self._publish("ZoneDisabled", name, f"zone disabled: {name}")

    def rollback_zone(self, name: str, version: int, reason: str) -> str:
        result = self.manager.rollback(name, version, reason)
        self._publish("ZoneRollback", name, f"zone rollback: {name} -> {version}", {"version": version})
        return result

    def _publish(self, event_type: str, subject: str, message: str, payload: dict | None = None) -> None:
        event = AuditEvent(event_type=event_type, category="zone", subject=subject, message=message, payload=payload or {})
        self.event_bus.publish(event)
        if self.audit is not None:
            self.audit.append(event)
