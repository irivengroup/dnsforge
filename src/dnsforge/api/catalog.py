from __future__ import annotations

from dnsforge.application.catalog.catalog_service import CatalogService
from dnsforge.application.events.event_bus import EventBus
from dnsforge.domain.events.model import AuditEvent
from dnsforge.infrastructure.audit.event_repository import AuditEventRepository
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class CatalogApi:
    def __init__(self, paths: ProjectPaths, event_bus: EventBus | None = None, audit: AuditEventRepository | None = None) -> None:
        self.service = CatalogService(paths)
        self.event_bus = event_bus or EventBus()
        self.audit = audit

    def status(self) -> str:
        return self.service.status()

    def sync(self, reason: str) -> str:
        result = self.service.sync(reason)
        self._publish("CatalogSynced", result)
        return result

    def repair(self, reason: str) -> str:
        result = self.service.repair(reason)
        self._publish("CatalogRepaired", result)
        return result

    def validate(self) -> str:
        return self.service.validate()

    def _publish(self, event_type: str, message: str) -> None:
        event = AuditEvent(event_type=event_type, category="catalog", subject="catalog", message=message)
        self.event_bus.publish(event)
        if self.audit is not None:
            self.audit.append(event)
