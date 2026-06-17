from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class ConfigSnapshot:
    identifier: int
    timestamp: datetime
    reason: str
    checksum: str
    dnsforge_version: str
    content: str
    path: Path | None = None

    def title(self) -> str:
        return f"{self.identifier}\t{self.timestamp.isoformat()}\t{self.checksum}\t{self.reason}"
