from __future__ import annotations

from pathlib import Path

from dnsforge.application.events.event_bus import EventBus
from dnsforge.application.migration.migration_service import MigrationService
from dnsforge.domain.events.model import AuditEvent
from dnsforge.domain.migration.model import MigrationTarget
from dnsforge.infrastructure.audit.event_repository import AuditEventRepository
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class MigrationApi:
    """Internal facade for local proxy profile migrations.

    The API is an additional entry point for future adapters. The local CLI remains
    a first-class interface and calls the same application services directly.
    """

    def __init__(
        self, paths: ProjectPaths, event_bus: EventBus | None = None, audit: AuditEventRepository | None = None
    ) -> None:
        self.paths = paths
        self.service = MigrationService(paths)
        self.event_bus = event_bus or EventBus()
        self.audit = audit

    def migrate(
        self,
        setup_file: Path,
        target: str | MigrationTarget,
        reason: str,
        target_root: Path = Path("/"),
        dry_run: bool = False,
    ) -> str:
        migration_target = target if isinstance(target, MigrationTarget) else MigrationTarget.from_value(target)
        self._publish("MigrationStarted", migration_target.value, f"migration started: {migration_target.value}")
        try:
            result = self.service.migrate(
                setup_file,
                migration_target,
                dry_run=dry_run,
                reason=reason,
                target_root=target_root,
            )
        except Exception as exc:
            self._publish("MigrationFailed", migration_target.value, str(exc))
            raise
        self._publish("MigrationCompleted", migration_target.value, result)
        return result

    def _publish(self, event_type: str, subject: str, message: str) -> None:
        event = AuditEvent(event_type=event_type, category="migration", subject=subject, message=message)
        self.event_bus.publish(event)
        if self.audit is not None:
            self.audit.append(event)
