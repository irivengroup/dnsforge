from __future__ import annotations

from pathlib import Path

from dnsforge.application.disaster.disaster_service import DisasterRecoveryService
from dnsforge.application.events.event_bus import EventBus
from dnsforge.domain.events.model import AuditEvent
from dnsforge.infrastructure.audit.event_repository import AuditEventRepository
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class DisasterRecoveryApi:
    def __init__(self, paths: ProjectPaths, event_bus: EventBus | None = None, audit: AuditEventRepository | None = None) -> None:
        self.service = DisasterRecoveryService(paths)
        self.event_bus = event_bus or EventBus()
        self.audit = audit

    def snapshot(self, reason: str, target_root: Path = Path("/")) -> str:
        result = self.service.snapshot(reason, target_root=target_root)
        self._publish("DisasterSnapshotCreated", result)
        return result

    def restore(self, snapshot: Path, target_root: Path = Path("/"), dry_run: bool = False) -> str:
        result = self.service.restore(snapshot, target_root=target_root, dry_run=dry_run)
        self._publish("DisasterRestoreCompleted", result)
        return result

    def verify(self, snapshot: Path) -> str:
        return self.service.verify(snapshot)

    def _publish(self, event_type: str, message: str) -> None:
        event = AuditEvent(event_type=event_type, category="disaster", subject="disaster", message=message)
        self.event_bus.publish(event)
        if self.audit is not None:
            self.audit.append(event)
