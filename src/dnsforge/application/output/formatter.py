from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol


@dataclass(frozen=True)
class OutputEnvelope:
    """Stable DNSForge command output envelope."""

    status: str
    data: Any
    timestamp: str

    @classmethod
    def success(cls, data: Any) -> "OutputEnvelope":
        return cls(status="success", data=data, timestamp=datetime.now(timezone.utc).isoformat())

    @classmethod
    def error(cls, data: Any) -> "OutputEnvelope":
        return cls(status="error", data=data, timestamp=datetime.now(timezone.utc).isoformat())

    def as_dict(self) -> dict[str, Any]:
        return {"status": self.status, "timestamp": self.timestamp, "data": self.data}


class OutputFormatter(Protocol):
    """Formatter contract shared by CLI and future API presentation layers."""

    def render(self, envelope: OutputEnvelope) -> str: ...
