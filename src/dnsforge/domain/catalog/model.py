from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from dnsforge.shared.errors import DnsForgeError


class CatalogState(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"

    @classmethod
    def from_value(cls, value: str) -> "CatalogState":
        for item in cls:
            if item.value == value:
                return item
        raise DnsForgeError(f"invalid catalog state: {value}")


@dataclass(frozen=True)
class CatalogZoneEntry:
    zone_name: str
    zone_type: str
    views: list[str]
    member_name: str


@dataclass(frozen=True)
class CatalogStateDocument:
    state: CatalogState = CatalogState.DISABLED
    last_reason: str = ""
    entries: list[CatalogZoneEntry] | None = None

    def active_entries(self) -> list[CatalogZoneEntry]:
        return list(self.entries or [])
