from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import ipaddress
from dnsforge.shared.errors import ZoneError

class DnsRecordType(str, Enum):
    A="A"; AAAA="AAAA"; CNAME="CNAME"; MX="MX"; TXT="TXT"; NS="NS"; PTR="PTR"; SRV="SRV"; CAA="CAA"
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
        if not self.name: raise ZoneError("record name is mandatory")
        if not self.value: raise ZoneError("record value is mandatory")
        if self.ttl is not None and self.ttl <= 0: raise ZoneError("ttl must be positive")
        if self.record_type is DnsRecordType.A: ipaddress.IPv4Address(self.value)
        if self.record_type is DnsRecordType.AAAA: ipaddress.IPv6Address(self.value)
        if self.record_type in {DnsRecordType.MX, DnsRecordType.SRV} and self.priority is None:
            raise ZoneError(f"{self.record_type.value} requires priority")

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
