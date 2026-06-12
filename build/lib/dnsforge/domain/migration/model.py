from __future__ import annotations

from enum import Enum


class MigrationTarget(str, Enum):
    PROXY_FORWARDER = "proxy-forwarder"
    PROXY_HYBRID = "proxy-hybrid"

    @classmethod
    def from_value(cls, value: str) -> "MigrationTarget":
        for item in cls:
            if item.value == value:
                return item
        raise ValueError("unsupported migration target. Allowed: proxy-forwarder, proxy-hybrid")
