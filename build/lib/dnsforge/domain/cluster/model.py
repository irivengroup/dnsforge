from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ClusterRole(str, Enum):
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
    AUTHORITATIVE_HA = "authoritative-ha"


@dataclass(frozen=True)
class ClusterConfig:
    enabled: bool
    role: ClusterRole | None
    name: str
    local_node: str
    peers: list[str]
    dns_role: str = ""
    vip: str | None = None
    interface: str | None = None
    priority: int = 100
    vrid: int = 53
    auth_pass: str | None = None

    @property
    def mode(self) -> ClusterMode:
        if not self.enabled:
            return ClusterMode.DISABLED
        return ClusterMode.AUTHORITATIVE_HA

    @property
    def node_count(self) -> int:
        return 1 + len(self.peers) if self.enabled else 0

    @property
    def keepalived_state(self) -> str:
        return "MASTER" if self.priority >= 150 else "BACKUP"
