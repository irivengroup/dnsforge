from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
@dataclass(frozen=True)
class ZoneSnapshot:
    zone: str
    version: int
    timestamp: datetime
    action: str
    content: str
    path: Path|None=None
    def title(self)->str:
        return f"{self.version}\t{self.timestamp.isoformat()}\t{self.action}"
