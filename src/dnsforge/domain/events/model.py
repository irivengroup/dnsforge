from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    category: str
    message: str
    subject: str = ""
    severity: str = "info"
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: uuid4().hex)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "created_at": self.created_at,
            "event_type": self.event_type,
            "category": self.category,
            "subject": self.subject,
            "severity": self.severity,
            "message": self.message,
            "payload": dict(self.payload),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)
