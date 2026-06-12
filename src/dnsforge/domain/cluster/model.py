from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ClusterRole(str, Enum):
    PROXY = "proxy"
    AUTHORITATIVE = "authoritative"

    @classmethod
    def from_value(cls, value: str | None) -> "ClusterRole":
        normalized = (value or "").strip().strip("'\"").lower()
        for item in cls:
            if item.value == normalized:
                return item
        raise ValueError(f"invalid cluster role: {value}")


class ClusterMode(str, Enum):
    DISABLED = "disabled"
    PROXY_VIP = "proxy-vip"
    AUTHORITATIVE_REPLICATION = "authoritative-replication"


@dataclass(frozen=True)
class ClusterConfig:
    enabled: bool
    role: ClusterRole | None
    name: str
    local_node: str
    peers: list[str]
    vip: str | None = None
    interface: str | None = None
    priority: int = 100
    auth_pass: str | None = None

    @property
    def mode(self) -> ClusterMode:
        if not self.enabled:
            return ClusterMode.DISABLED
        if self.role is ClusterRole.PROXY:
            return ClusterMode.PROXY_VIP
        return ClusterMode.AUTHORITATIVE_REPLICATION
