from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from dnsforge.domain.events.model import AuditEvent


class AuditEventRepository:
    """Append-only JSONL repository for critical product events."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, event: AuditEvent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(event.to_json() + "\n")

    def list(self, category: str | None = None) -> list[AuditEvent]:
        if not self.path.exists():
            return []
        events: list[AuditEvent] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            if category is not None and data.get("category") != category:
                continue
            events.append(
                AuditEvent(
                    event_type=data["event_type"],
                    category=data["category"],
                    message=data["message"],
                    subject=data.get("subject", ""),
                    severity=data.get("severity", "info"),
                    payload=dict(data.get("payload", {})),
                    event_id=data["event_id"],
                    created_at=data["created_at"],
                )
            )
        return events

    def extend(self, events: Iterable[AuditEvent]) -> None:
        for event in events:
            self.append(event)
