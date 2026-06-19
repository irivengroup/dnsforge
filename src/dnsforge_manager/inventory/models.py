from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class NodeRole(str, Enum):
    AUTHORITATIVE = "authoritative"
    PROXY_FORWARDER = "proxy-forwarder"
    PROXY_HYBRID = "proxy-hybrid"


class NodeStatus(str, Enum):
    REGISTERED = "registered"
    UNREACHABLE = "unreachable"
    HEALTHY = "healthy"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class ManagedNode:
    node_id: str
    name: str
    api_endpoint: str
    role: NodeRole
    site: str = "default"
    environment: str = "production"
    cluster_id: str | None = None
    status: NodeStatus = NodeStatus.REGISTERED
    labels: dict[str, str] = field(default_factory=dict)

    def requires_dnsforge_agent(self) -> bool:
        return True
