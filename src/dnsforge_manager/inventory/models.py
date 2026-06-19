from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum


class NodeRole(str, Enum):
    AUTHORITATIVE = "authoritative"
    PROXY_FORWARDER = "proxy-forwarder"
    PROXY_HYBRID = "proxy-hybrid"


class NodeStatus(str, Enum):
    REGISTERED = "registered"
    ACTIVE = "active"
    UNREACHABLE = "unreachable"
    DISABLED = "disabled"
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
    agent_token: str | None = field(default=None, compare=False)
    labels: dict[str, str] = field(default_factory=dict)

    def requires_dnsforge_agent(self) -> bool:
        return True

    def to_dict(self, *, include_token: bool = False) -> dict[str, object]:
        data = asdict(self)
        data["role"] = self.role.value
        data["status"] = self.status.value
        if not include_token:
            data.pop("agent_token", None)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> ManagedNode:
        node_data = dict(data)
        role = NodeRole(str(node_data.pop("role")))
        status = NodeStatus(str(node_data.pop("status", NodeStatus.REGISTERED.value)))
        labels = node_data.pop("labels", {})
        if not isinstance(labels, dict):
            raise ValueError("node labels must be a mapping")
        return cls(
            node_id=str(node_data.pop("node_id")),
            name=str(node_data.pop("name")),
            api_endpoint=str(node_data.pop("api_endpoint")),
            role=role,
            site=str(node_data.pop("site", "default")),
            environment=str(node_data.pop("environment", "production")),
            cluster_id=(None if node_data.get("cluster_id") is None else str(node_data.pop("cluster_id"))),
            status=status,
            agent_token=(None if node_data.get("agent_token") is None else str(node_data.pop("agent_token"))),
            labels={str(key): str(value) for key, value in labels.items()},
        )
