from __future__ import annotations

import datetime as dt
from pathlib import Path

from dnsforge.shared.errors import SettingsError


class SecurityHistoryService:
    """Append-only security history with explicit rollback markers.

    DNSForge security controls are derived from setup.conf and rendered BIND
    configuration, not from a mutable security database. A security rollback
    therefore cannot safely mutate state from this service alone. Instead, the
    command validates that a referenced security history entry exists and records
    an auditable rollback marker that operators can correlate with the matching
    configuration rollback.
    """

    def __init__(self, root: Path = Path("/var/backups/dnsforge/security/history")) -> None:
        self.root = root

    def record(self, action: str, detail: str = "") -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
        safe_action = self._safe_action(action)
        path = self.root / f"{stamp}-{safe_action}.log"
        path.write_text(f"timestamp={stamp}\naction={safe_action}\ndetail={detail}\n", encoding="utf-8")
        return path

    def history(self) -> str:
        entries = self._entries()
        if not entries:
            return "Security history: none"
        lines = ["Security history", "ID\tEntry"]
        lines.extend(f"{index}\t{path.name}" for index, path in enumerate(entries, start=1))
        return "\n".join(lines)

    def rollback(self, version: str | None = None) -> str:
        entries = self._entries()
        if not entries:
            raise SettingsError("security rollback requires at least one security history entry")

        selected = self._select_entry(entries, version)
        marker = self.record("rollback-marker", f"selected={selected.name}")
        return f"Security rollback marker created: {marker.name}; selected={selected.name}"

    def _entries(self) -> list[Path]:
        if not self.root.exists():
            return []
        return sorted(path for path in self.root.glob("*.log") if path.is_file())

    def _select_entry(self, entries: list[Path], version: str | None) -> Path:
        if version is None or version == "latest":
            return entries[-1]
        clean = version.strip()
        if clean.isdigit():
            index = int(clean)
            if 1 <= index <= len(entries):
                return entries[index - 1]
        for entry in entries:
            if entry.name == clean or entry.stem == clean:
                return entry
        raise SettingsError(f"security history entry not found: {version}")

    def _safe_action(self, action: str) -> str:
        safe = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in action.strip())
        return safe.strip("-") or "security-event"
