from __future__ import annotations

from pathlib import Path

from dnsforge.infrastructure.audit.event_repository import AuditEventRepository


class EventTailService:
    def __init__(self, repository_path: Path) -> None:
        self.repository = AuditEventRepository(repository_path)

    def tail(self, *, limit: int = 20, category: str | None = None) -> str:
        events = self.repository.list(category=category)[-limit:]
        rows = []
        for event in events:
            rows.append(
                f"{event.created_at}\t{event.severity.upper()}\t{event.category}\t{event.event_type}\t{event.subject}\t{event.message}"
            )
        return "\n".join(rows)
