from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

from dnsforge.domain.zone.record import DnsRecord
from dnsforge.shared.errors import ZoneError

_ZONE_LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,62}$")


class ZoneType(str, Enum):
    MASTER = "master"
    SECONDARY = "secondary"
    FORWARD = "forward"

    @classmethod
    def from_value(cls, value: str) -> "ZoneType":
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"invalid zone type: {value}")


@dataclass(frozen=True)
class ZoneDefinition:
    name: str
    zone_type: ZoneType
    views: list[str]
    cluster: str | None = None
    enabled: bool = True
    acl: dict[str, str] = field(default_factory=dict)
    records: list[DnsRecord] = field(default_factory=list)
    managed_reverse: bool = False

    def validate(self) -> None:
        self._validate_zone_name()
        if not self.views:
            raise ZoneError("zone must have at least one view")
        for view in self.views:
            if view not in {"internal", "external", "partner"}:
                raise ZoneError(f"unsupported zone view/scope: {view}")
        if self.zone_type in {ZoneType.SECONDARY, ZoneType.FORWARD} and self.records:
            raise ZoneError(f"{self.zone_type.value} zones must not carry master zone records")
        self._validate_record_set()

    def _validate_zone_name(self) -> None:
        name = self.name.rstrip(".")
        if not name or len(name) > 253 or any(ch.isspace() for ch in name):
            raise ZoneError(f"invalid zone name: {self.name}")
        if name.endswith("in-addr.arpa") or name.endswith("ip6.arpa"):
            return
        for label in name.split("."):
            if not _ZONE_LABEL_RE.match(label):
                raise ZoneError(f"invalid zone name: {self.name}")

    def _validate_record_set(self) -> None:
        cname_owners: set[str] = set()
        non_cname_owners: set[str] = set()
        for record in self.records:
            record.validate()
            owner = record.name.lower()
            if record.record_type.value == "CNAME":
                cname_owners.add(owner)
            else:
                non_cname_owners.add(owner)
        conflicts = cname_owners & non_cname_owners
        if conflicts:
            raise ZoneError(f"CNAME owner cannot coexist with other records: {', '.join(sorted(conflicts))}")
