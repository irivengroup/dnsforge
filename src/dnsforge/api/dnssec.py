from __future__ import annotations

from pathlib import Path

from dnsforge.application.events.event_bus import EventBus
from dnsforge.application.security.dnssec.dnssec_service import DnssecService
from dnsforge.domain.events.model import AuditEvent
from dnsforge.infrastructure.audit.event_repository import AuditEventRepository


class DnssecApi:
    def __init__(self, setup_file: Path, event_bus: EventBus | None = None, audit: AuditEventRepository | None = None) -> None:
        self.setup_file = setup_file
        self.service = DnssecService()
        self.event_bus = event_bus or EventBus()
        self.audit = audit

    def status(self, zone: str | None = None) -> str:
        return self.service.status(self.setup_file, zone)

    def enable(self, zone: str, reason: str) -> str:
        result = self.service.enable(self.setup_file, zone, reason)
        self._publish("DnssecEnabled", zone, result)
        return result

    def disable(self, zone: str, reason: str) -> str:
        result = self.service.disable(self.setup_file, zone, reason)
        self._publish("DnssecDisabled", zone, result)
        return result

    def rotate_ksk(self, zone: str, reason: str) -> str:
        result = self.service.rotate_ksk(self.setup_file, zone, reason)
        self._publish("DnssecKskRotated", zone, result)
        return result

    def rotate_zsk(self, zone: str, reason: str) -> str:
        result = self.service.rotate_zsk(self.setup_file, zone, reason)
        self._publish("DnssecZskRotated", zone, result)
        return result

    def _publish(self, event_type: str, subject: str, message: str) -> None:
        event = AuditEvent(event_type=event_type, category="dnssec", subject=subject, message=message)
        self.event_bus.publish(event)
        if self.audit is not None:
            self.audit.append(event)
