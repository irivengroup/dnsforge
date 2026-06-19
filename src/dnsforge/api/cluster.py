from __future__ import annotations

from pathlib import Path

from dnsforge.application.cluster.cluster_service import ClusterService
from dnsforge.application.events.event_bus import EventBus
from dnsforge.domain.events.model import AuditEvent
from dnsforge.infrastructure.audit.event_repository import AuditEventRepository


class ClusterApi:
    def __init__(self, setup_file: Path, event_bus: EventBus | None = None, audit: AuditEventRepository | None = None) -> None:
        self.setup_file = setup_file
        self.service = ClusterService()
        self.event_bus = event_bus or EventBus()
        self.audit = audit

    def status(self) -> str:
        return self.service.status(self.setup_file)

    def validate(self) -> str:
        return self.service.validate(self.setup_file)

    def audit_cluster(self, output_format: str = "text") -> tuple[bool, str]:
        ok, output = self.service.audit(self.setup_file, output_format=output_format)
        self._publish("ClusterAuditCompleted", "Cluster audit OK" if ok else "Cluster audit failed", "info" if ok else "error")
        return ok, output

    def sync(self, reason: str, dry_run: bool = False) -> str:
        result = self.service.sync(self.setup_file, reason, dry_run=dry_run)
        self._publish("ClusterSynced", result)
        return result

    def _publish(self, event_type: str, message: str, severity: str = "info") -> None:
        event = AuditEvent(event_type=event_type, category="cluster", subject="cluster", message=message, severity=severity)
        self.event_bus.publish(event)
        if self.audit is not None:
            self.audit.append(event)
