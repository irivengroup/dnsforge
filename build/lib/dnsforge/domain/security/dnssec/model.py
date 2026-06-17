from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum

from dnsforge.shared.errors import DnsForgeError


class DnssecZoneState(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    SIGNED = "signed"

    @classmethod
    def from_value(cls, value: str) -> "DnssecZoneState":
        for item in cls:
            if item.value == value:
                return item
        raise DnsForgeError(f"invalid DNSSEC zone state: {value}")


@dataclass(frozen=True)
class DnssecKeyMetadata:
    key_id: str
    key_type: str
    algorithm: str
    created_at: str
    expires_at: str


@dataclass(frozen=True)
class DnssecZoneMetadata:
    zone: str
    state: DnssecZoneState = DnssecZoneState.DISABLED
    ksk: DnssecKeyMetadata | None = None
    zsk: DnssecKeyMetadata | None = None
    signed_at: str = ""
    last_reason: str = ""
    history: list[str] = field(default_factory=list)

    def enabled(self) -> bool:
        return self.state in {DnssecZoneState.ENABLED, DnssecZoneState.SIGNED}


def require_dnssec_reason(reason: str) -> str:
    normalized = (reason or "").strip()
    if len(normalized) < 8:
        raise DnsForgeError("--reason is required and must contain at least 8 characters")
    return normalized


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)
