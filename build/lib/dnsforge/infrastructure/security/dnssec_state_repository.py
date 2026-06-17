from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from dnsforge.domain.security.dnssec.model import (
    DnssecKeyMetadata,
    DnssecZoneMetadata,
    DnssecZoneState,
)


class DnssecStateRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def list(self) -> list[DnssecZoneMetadata]:
        data = self._read()
        return [self._zone(item) for item in data.get("zones", [])]

    def get(self, zone: str) -> DnssecZoneMetadata:
        for item in self.list():
            if item.zone == zone:
                return item
        return DnssecZoneMetadata(zone=zone)

    def save(self, zone: DnssecZoneMetadata) -> None:
        zones = [item for item in self.list() if item.zone != zone.zone]
        zones.append(zone)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps({"zones": [self._dict(item) for item in sorted(zones, key=lambda item: item.zone)]}, indent=2)
            + "\n",
            encoding="utf-8",
        )

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"zones": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _dict(self, zone: DnssecZoneMetadata) -> dict[str, Any]:
        return asdict(zone) | {"state": zone.state.value}

    def _key(self, data: dict[str, Any] | None) -> DnssecKeyMetadata | None:
        if not data:
            return None
        return DnssecKeyMetadata(
            key_id=str(data.get("key_id", "")),
            key_type=str(data.get("key_type", "")),
            algorithm=str(data.get("algorithm", "")),
            created_at=str(data.get("created_at", "")),
            expires_at=str(data.get("expires_at", "")),
        )

    def _zone(self, data: dict[str, Any]) -> DnssecZoneMetadata:
        return DnssecZoneMetadata(
            zone=str(data.get("zone", "")),
            state=DnssecZoneState.from_value(str(data.get("state", "disabled"))),
            ksk=self._key(data.get("ksk")),
            zsk=self._key(data.get("zsk")),
            signed_at=str(data.get("signed_at", "")),
            last_reason=str(data.get("last_reason", "")),
            history=[str(item) for item in data.get("history", [])],
        )
