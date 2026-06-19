from __future__ import annotations

import json
from dnsforge_manager.domain.audit.models import ManagerAuditEvent
from pathlib import Path


class ManagerAuditRepository:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self._events: list[ManagerAuditEvent] = []
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: ManagerAuditEvent) -> ManagerAuditEvent:
        if self.path is None:
            self._events.append(event)
            return event
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.to_dict(), sort_keys=True) + "\n")
        return event

    def list(self) -> tuple[ManagerAuditEvent, ...]:
        if self.path is None:
            return tuple(self._events)
        if not self.path.exists():
            return ()
        events: list[ManagerAuditEvent] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            events.append(
                ManagerAuditEvent(
                    actor=str(payload["actor"]),
                    action=str(payload["action"]),
                    target=str(payload["target"]),
                    result=str(payload["result"]),
                    timestamp=str(payload["timestamp"]),
                    metadata=dict(payload.get("metadata", {})),
                )
            )
        return tuple(events)
