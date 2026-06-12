from __future__ import annotations
from pathlib import Path
import ipaddress
import json


class AclService:
    def __init__(self, path: Path = Path("/etc/dnsforge/acls.json")) -> None:
        self.path = path

    def _load(self) -> dict[str, list[str]]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data: dict[str, list[str]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def list(self) -> str:
        data = self._load()
        return "\n".join(sorted(data)) if data else "No ACL"

    def show(self, name: str) -> str:
        data = self._load()
        return "\n".join(data.get(name, [])) if data.get(name) else f"ACL not found: {name}"

    def create(self, name: str) -> str:
        data = self._load()
        data.setdefault(name, [])
        self._save(data)
        return f"ACL created: {name}"

    def delete(self, name: str) -> str:
        data = self._load()
        data.pop(name, None)
        self._save(data)
        return f"ACL deleted: {name}"

    def add_network(self, name: str, network: str) -> str:
        ipaddress.ip_network(network, strict=False)
        data = self._load()
        data.setdefault(name, [])
        if network not in data[name]:
            data[name].append(network)
        self._save(data)
        return f"Network added to ACL {name}: {network}"

    def remove_network(self, name: str, network: str) -> str:
        data = self._load()
        if name in data and network in data[name]:
            data[name].remove(network)
        self._save(data)
        return f"Network removed from ACL {name}: {network}"
