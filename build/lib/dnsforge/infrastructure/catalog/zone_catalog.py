from __future__ import annotations

from pathlib import Path
from typing import Any, List
from dnsforge.domain.zone.model import ZoneDefinition, ZoneLifecycleState, ZoneType
from dnsforge.domain.zone.record import DnsRecord, DnsRecordType
from dnsforge.shared.errors import ZoneError


class ZoneCatalog:
    def __init__(self, path: Path) -> None:
        self.path = path

    def list(self) -> List[ZoneDefinition]:
        if not self.path.exists():
            return []
        zones: List[ZoneDefinition] = []
        current: dict[str, Any] | None = None
        section: str | None = None
        rec: dict[str, Any] | None = None
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            s = raw.strip()
            if not s or s.startswith("#") or s == "zones:":
                continue
            if s.startswith("- name:"):
                if rec is not None and current is not None:
                    current["records"].append(self._record(rec))
                    rec = None
                if current is not None:
                    zones.append(self._zone(current))
                current = {
                    "name": s.split(":", 1)[1].strip(),
                    "type": "master",
                    "views": [],
                    "acl": {},
                    "enabled": True,
                    "records": [],
                    "managed_reverse": False,
                    "description": "",
                    "business_owner": "",
                    "technical_owner": "",
                    "environment": "",
                    "classification": "",
                    "lifecycle": "active",
                }
                section = None
                continue
            if current is None:
                continue
            if section == "records" and s.startswith("- type:"):
                if rec:
                    current["records"].append(self._record(rec))
                rec = {"type": s.split(":", 1)[1].strip()}
                continue
            if section == "records" and rec is not None:
                if ":" in s:
                    k, v = s.split(":", 1)
                    rec[k.strip()] = v.strip()
                continue
            if s.startswith("type:"):
                current["type"] = s.split(":", 1)[1].strip()
                section = None
            elif s.startswith("cluster:"):
                current["cluster"] = s.split(":", 1)[1].strip()
                section = None
            elif s.startswith("enabled:"):
                current["enabled"] = s.split(":", 1)[1].strip().lower() not in {"false", "no", "0"}
                section = None
            elif s.startswith("managed_reverse:"):
                current["managed_reverse"] = s.split(":", 1)[1].strip().lower() in {"true", "yes", "1"}
                section = None
            elif s.startswith("description:"):
                current["description"] = s.split(":", 1)[1].strip()
                section = None
            elif s.startswith("business_owner:"):
                current["business_owner"] = s.split(":", 1)[1].strip()
                section = None
            elif s.startswith("technical_owner:"):
                current["technical_owner"] = s.split(":", 1)[1].strip()
                section = None
            elif s.startswith("environment:"):
                current["environment"] = s.split(":", 1)[1].strip()
                section = None
            elif s.startswith("classification:"):
                current["classification"] = s.split(":", 1)[1].strip()
                section = None
            elif s.startswith("lifecycle:"):
                current["lifecycle"] = s.split(":", 1)[1].strip()
                section = None
            elif s == "views:":
                section = "views"
            elif s == "acl:":
                section = "acl"
            elif s == "records:":
                section = "records"
            elif s.startswith("- ") and section == "views":
                current["views"].append(s[2:].strip())
            elif ":" in s and section == "acl":
                k, v = s.split(":", 1)
                current["acl"][k.strip()] = v.strip()
        if rec is not None and current is not None:
            current["records"].append(self._record(rec))
        if current is not None:
            zones.append(self._zone(current))
        return zones

    def get(self, name: str) -> ZoneDefinition:
        for z in self.list():
            if z.name == name:
                return z
        raise ZoneError(f"zone not found: {name}")

    def create(self, zone: ZoneDefinition) -> None:
        zone.validate()
        zones = self.list()
        if any(z.name == zone.name for z in zones):
            raise ZoneError(f"zone already exists: {zone.name}")
        zones.append(zone)
        self.save(zones)

    def update(self, zone: ZoneDefinition) -> None:
        zones = []
        found = False
        for z in self.list():
            if z.name == zone.name:
                zones.append(zone)
                found = True
            else:
                zones.append(z)
        if not found:
            raise ZoneError(f"zone not found: {zone.name}")
        self.save(zones)

    def enable(self, name: str) -> None:
        self._enabled(name, True)

    def disable(self, name: str) -> None:
        self._enabled(name, False)

    def delete(self, name: str) -> None:
        zones = self.list()
        if not any(z.name == name for z in zones):
            raise ZoneError(f"zone not found: {name}")
        self.save([z for z in zones if z.name != name])

    def _enabled(self, name: str, enabled: bool) -> None:
        z = self.get(name)
        self.update(
            ZoneDefinition(
                z.name,
                z.zone_type,
                z.views,
                z.cluster,
                enabled,
                z.acl,
                z.records,
                z.managed_reverse,
                z.description,
                z.business_owner,
                z.technical_owner,
                z.environment,
                z.classification,
                z.lifecycle,
            )
        )

    def save(self, zones: List[ZoneDefinition]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lines = ["zones:"]
        for z in zones:
            lines += ["", f"  - name: {z.name}", f"    type: {z.zone_type.value}"]
            if z.cluster:
                lines.append(f"    cluster: {z.cluster}")
            lines.append(f"    managed_reverse: {'yes' if z.managed_reverse else 'no'}")
            lines.append(f"    description: {z.description}")
            lines.append(f"    business_owner: {z.business_owner}")
            lines.append(f"    technical_owner: {z.technical_owner}")
            lines.append(f"    environment: {z.environment}")
            lines.append(f"    classification: {z.classification}")
            lines.append(f"    lifecycle: {z.lifecycle.value}")
            lines += [f"    enabled: {'yes' if z.enabled else 'no'}", "    views:"]
            lines += [f"      - {v}" for v in z.views]
            lines.append("    acl:")
            acl = z.acl or {v: ("any;" if v == "external" else "recursive_clients;") for v in z.views}
            lines += [f"      {k}: {v}" for k, v in acl.items()]
            lines.append("    records:")
            for r in z.records:
                lines.append(f"      - type: {r.record_type.value}")
                lines.append(f"        name: {r.name}")
                if r.ttl is not None:
                    lines.append(f"        ttl: {r.ttl}")
                if r.priority is not None:
                    lines.append(f"        priority: {r.priority}")
                lines.append(f"        value: {r.value}")
        self.path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    def _zone(self, d: dict[str, Any]) -> ZoneDefinition:
        return ZoneDefinition(
            str(d["name"]),
            ZoneType.from_value(str(d.get("type", "master"))),
            [str(x) for x in d.get("views", [])],
            str(d["cluster"]) if d.get("cluster") else None,
            bool(d.get("enabled", True)),
            dict(d.get("acl", {})),
            list(d.get("records", [])),
            bool(d.get("managed_reverse", False)),
            str(d.get("description", "")),
            str(d.get("business_owner", "")),
            str(d.get("technical_owner", "")),
            str(d.get("environment", "")),
            str(d.get("classification", "")),
            ZoneLifecycleState.from_value(str(d.get("lifecycle", "active"))),
        )

    def _record(self, d: dict[str, Any]) -> DnsRecord:
        r = DnsRecord(
            DnsRecordType.from_value(str(d.get("type", ""))),
            str(d.get("name", "@")),
            str(d.get("value", "")),
            int(d["ttl"]) if d.get("ttl") else None,
            int(d["priority"]) if d.get("priority") else None,
        )
        r.validate()
        return r
