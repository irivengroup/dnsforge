from __future__ import annotations

from enum import Enum


class ProxyType(str, Enum):
    FORWARDER = "forwarder"
    HYBRID = "hybrid"

    @classmethod
    def choices(cls) -> list[str]:
        return [item.value for item in cls]

    @classmethod
    def from_value(cls, value: str) -> "ProxyType":
        for item in cls:
            if item.value == value:
                return item
        allowed = ", ".join(cls.choices())
        raise ValueError(f"invalid proxy type: {value}. Allowed values: {allowed}")

    @property
    def allows_local_authoritative_zones(self) -> bool:
        return self is ProxyType.HYBRID
