from __future__ import annotations
from pathlib import Path
import json


class ViewService:
    def __init__(self, path: Path = Path("/etc/dnsforge/views.json")) -> None:
        self.path = path

    def _load(self) -> dict[str, dict[str, list[str]]]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data: dict[str, dict[str, list[str]]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def list(self) -> str:
        data = self._load()
        return "\n".join(sorted(data)) if data else "No view"

    def create(self, name: str) -> str:
        data = self._load()
        data.setdefault(name, {"zones": []})
        self._save(data)
        return f"View created: {name}"

    def delete(self, name: str) -> str:
        data = self._load()
        data.pop(name, None)
        self._save(data)
        return f"View deleted: {name}"

    def attach_zone(self, name: str, zone: str) -> str:
        data = self._load()
        data.setdefault(name, {"zones": []})
        if zone not in data[name]["zones"]:
            data[name]["zones"].append(zone)
        self._save(data)
        return f"Zone attached to view {name}: {zone}"
