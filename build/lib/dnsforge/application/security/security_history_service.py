from __future__ import annotations

from pathlib import Path
import datetime as dt


class SecurityHistoryService:
    def __init__(self, root: Path = Path("/var/backups/dnsforge/security/history")) -> None:
        self.root = root

    def record(self, action: str, detail: str = "") -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
        path = self.root / f"{stamp}-{action}.log"
        path.write_text(f"timestamp={stamp}\naction={action}\ndetail={detail}\n", encoding="utf-8")
        return path

    def history(self) -> str:
        if not self.root.exists():
            return "Security history: none"
        return "\n".join(["Security history", *[p.name for p in sorted(self.root.glob("*.log"))]])

    def rollback(self, version: str | None = None) -> str:
        return f"Security rollback planned for {version or 'latest'}"
