from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from enum import Enum

from dnsforge.shared.errors import ZoneError

_LABEL_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_-]{0,62}$")
_HOST_LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,62}$")


class DnsRecordType(str, Enum):
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    TXT = "TXT"
    NS = "NS"
    PTR = "PTR"
    SRV = "SRV"
    CAA = "CAA"

    @classmethod
    def from_value(cls, value: str) -> "DnsRecordType":
        value = value.upper()
        for item in cls:
            if item.value == value:
                return item
        raise ZoneError(f"unsupported DNS record type: {value}")


@dataclass(frozen=True)
class DnsRecord:
    record_type: DnsRecordType
    name: str
    value: str
    ttl: int | None = None
    priority: int | None = None

    def validate(self) -> None:
        if not self.name:
            raise ZoneError("record name is mandatory")
        if not self.value:
            raise ZoneError("record value is mandatory")
        if self.ttl is not None and not (1 <= self.ttl <= 2147483647):
            raise ZoneError("ttl must be between 1 and 2147483647 seconds")
        self._validate_owner()
        if self.record_type is DnsRecordType.A:
            ipaddress.IPv4Address(self.value)
        elif self.record_type is DnsRecordType.AAAA:
            ipaddress.IPv6Address(self.value)
        elif self.record_type is DnsRecordType.CNAME:
            self._validate_domain_target(self.value, "CNAME target")
        elif self.record_type is DnsRecordType.MX:
            self._validate_priority_required()
            self._validate_domain_target(self.value, "MX exchange")
        elif self.record_type is DnsRecordType.NS:
            self._validate_domain_target(self.value, "NS target")
        elif self.record_type is DnsRecordType.PTR:
            self._validate_domain_target(self.value, "PTR target")
        elif self.record_type is DnsRecordType.SRV:
            self._validate_priority_required()
            self._validate_srv_value()
        elif self.record_type is DnsRecordType.CAA:
            if not self.value.strip():
                raise ZoneError("CAA value is mandatory")

    def _validate_owner(self) -> None:
        if self.name == "@":
            return
        labels = self.name.rstrip(".").split(".")
        for label in labels:
            if not label or len(label) > 63:
                raise ZoneError(f"invalid DNS owner label: {self.name}")
            if self.record_type is DnsRecordType.SRV:
                if not _LABEL_RE.match(label):
                    raise ZoneError(f"invalid SRV owner label: {self.name}")
            elif not _HOST_LABEL_RE.match(label):
                raise ZoneError(f"invalid DNS owner label: {self.name}")

    def _validate_domain_target(self, value: str, label: str) -> None:
        target = value.rstrip(".")
        if not target or len(target) > 253:
            raise ZoneError(f"invalid {label}: {value}")
        for item in target.split("."):
            if not _HOST_LABEL_RE.match(item):
                raise ZoneError(f"invalid {label}: {value}")

    def _validate_priority_required(self) -> None:
        if self.priority is None:
            raise ZoneError(f"{self.record_type.value} requires priority")
        if not (0 <= self.priority <= 65535):
            raise ZoneError(f"{self.record_type.value} priority must be between 0 and 65535")

    def _validate_srv_value(self) -> None:
        parts = self.value.split()
        if len(parts) != 3:
            raise ZoneError("SRV value must be: WEIGHT PORT TARGET")
        weight, port, target = parts
        if not (0 <= int(weight) <= 65535):
            raise ZoneError("SRV weight must be between 0 and 65535")
        if not (0 <= int(port) <= 65535):
            raise ZoneError("SRV port must be between 0 and 65535")
        self._validate_domain_target(target, "SRV target")

    def to_bind_line(self) -> str:
        ttl = f"{self.ttl} " if self.ttl else ""
        if self.priority is not None:
            return f"{self.name} {ttl}IN {self.record_type.value} {self.priority} {self.value}"
        return f"{self.name} {ttl}IN {self.record_type.value} {self.value}"


class DnsRecordExpressionParser:
    def parse_add(self, expression: str, ttl: int | None = None) -> DnsRecord:
        parts = expression.split(":")
        if len(parts) < 3:
            raise ZoneError("use TYPE:NAME:VALUE or MX:PRIORITY:VALUE")
        rtype = DnsRecordType.from_value(parts[0])
        if rtype in {DnsRecordType.MX, DnsRecordType.SRV}:
            rec = DnsRecord(rtype, "@", ":".join(parts[2:]), ttl=ttl, priority=int(parts[1]))
        else:
            rec = DnsRecord(rtype, parts[1], ":".join(parts[2:]), ttl=ttl)
        rec.validate()
        return rec

    def parse_update(self, expression: str, ttl: int | None = None) -> tuple[DnsRecord, str]:
        parts = expression.split(":")
        if len(parts) < 4:
            raise ZoneError("use TYPE:NAME:OLD_VALUE:NEW_VALUE")
        rtype = DnsRecordType.from_value(parts[0])
        if rtype in {DnsRecordType.MX, DnsRecordType.SRV}:
            rec = DnsRecord(rtype, "@", ":".join(parts[3:]), ttl=ttl, priority=int(parts[1]))
            old = parts[2]
        else:
            rec = DnsRecord(rtype, parts[1], ":".join(parts[3:]), ttl=ttl)
            old = parts[2]
        rec.validate()
        return rec, old

    def parse_delete(self, expression: str) -> tuple[DnsRecordType, str, int | None, str | None]:
        parts = expression.split(":")
        if len(parts) < 2:
            raise ZoneError("use TYPE:NAME or TYPE:NAME:VALUE")
        rtype = DnsRecordType.from_value(parts[0])
        if rtype in {DnsRecordType.MX, DnsRecordType.SRV}:
            return rtype, "@", int(parts[1]), ":".join(parts[2:]) if len(parts) > 2 else None
        return rtype, parts[1], None, ":".join(parts[2:]) if len(parts) > 2 else None
