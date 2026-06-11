from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from dnsforge.domain.zone.record import DnsRecord

class ZoneType(str, Enum):
    MASTER="master"; SECONDARY="secondary"; FORWARD="forward"
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

    def validate(self) -> None:
        if not self.name or any(ch.isspace() for ch in self.name): raise ValueError(f"invalid zone name: {self.name}")
        if not self.views: raise ValueError("zone must have at least one view")
        for record in self.records: record.validate()
