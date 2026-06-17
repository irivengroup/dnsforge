from __future__ import annotations

from pathlib import Path
from typing import Any

from dnsforge.domain.catalog.model import CatalogState, CatalogStateDocument, CatalogZoneEntry


class CatalogStateRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> CatalogStateDocument:
        if not self.path.exists():
            return CatalogStateDocument()
        data: dict[str, Any] = {"entries": []}
        current: dict[str, Any] | None = None
        section: str | None = None
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            s = raw.strip()
            if not s or s.startswith("#"):
                continue
            if s == "entries:":
                section = "entries"
                continue
            if section == "entries" and s.startswith("- zone:"):
                if current is not None:
                    data["entries"].append(self._entry(current))
                current = {"zone": s.split(":", 1)[1].strip(), "type": "master", "views": [], "member": ""}
                continue
            if section == "entries" and current is not None:
                if s == "views:":
                    section = "entry_views"
                    continue
                if ":" in s:
                    key, value = s.split(":", 1)
                    current[key.strip()] = value.strip()
                    continue
            if section == "entry_views" and current is not None:
                if s.startswith("- "):
                    current["views"].append(s[2:].strip())
                    continue
                section = "entries"
            if s.startswith("state:"):
                data["state"] = s.split(":", 1)[1].strip()
            elif s.startswith("last_reason:"):
                data["last_reason"] = s.split(":", 1)[1].strip()
        if current is not None:
            data["entries"].append(self._entry(current))
        return CatalogStateDocument(
            CatalogState.from_value(str(data.get("state", "disabled"))),
            str(data.get("last_reason", "")),
            list(data.get("entries", [])),
        )

    def save(self, document: CatalogStateDocument) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"state: {document.state.value}", f"last_reason: {document.last_reason}", "entries:"]
        for entry in document.active_entries():
            lines.extend(
                [
                    f"  - zone: {entry.zone_name}",
                    f"    type: {entry.zone_type}",
                    f"    member: {entry.member_name}",
                    "    views:",
                ]
            )
            lines.extend(f"      - {view}" for view in entry.views)
        self.path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    def _entry(self, data: dict[str, Any]) -> CatalogZoneEntry:
        return CatalogZoneEntry(
            str(data.get("zone", "")),
            str(data.get("type", "master")),
            [str(item) for item in data.get("views", [])],
            str(data.get("member") or data.get("zone", "")),
        )
