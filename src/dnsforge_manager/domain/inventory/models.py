from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


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


class AgentReadiness(str, Enum):
    READY = "READY"
    WARNING = "WARNING"
    FAILED = "FAILED"


@dataclass(frozen=True)
class Site:
    site_id: str
    name: str
    description: str = ""
    labels: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Site":
        labels = data.get("labels", {})
        if not isinstance(labels, dict):
            raise ValueError("site labels must be a mapping")
        return cls(
            site_id=str(data["site_id"]),
            name=str(data.get("name", data["site_id"])),
            description=str(data.get("description", "")),
            labels={str(k): str(v) for k, v in labels.items()},
        )


@dataclass(frozen=True)
class Environment:
    environment_id: str
    name: str
    description: str = ""
    labels: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Environment":
        labels = data.get("labels", {})
        if not isinstance(labels, dict):
            raise ValueError("environment labels must be a mapping")
        return cls(
            environment_id=str(data["environment_id"]),
            name=str(data.get("name", data["environment_id"])),
            description=str(data.get("description", "")),
            labels={str(k): str(v) for k, v in labels.items()},
        )


@dataclass(frozen=True)
class Cluster:
    cluster_id: str
    name: str
    site: str
    environment: str = "production"
    description: str = ""
    labels: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Cluster":
        labels = data.get("labels", {})
        if not isinstance(labels, dict):
            raise ValueError("cluster labels must be a mapping")
        return cls(
            cluster_id=str(data["cluster_id"]),
            name=str(data.get("name", data["cluster_id"])),
            site=str(data.get("site", "default")),
            environment=str(data.get("environment", "production")),
            description=str(data.get("description", "")),
            labels={str(k): str(v) for k, v in labels.items()},
        )


@dataclass(frozen=True)
class AgentStatus:
    fingerprint: str
    readiness: AgentReadiness
    hostname: str = ""
    version: str = ""
    profile: str = ""
    site: str = "default"
    cluster: str | None = None
    message: str = ""
    checks: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["readiness"] = self.readiness.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "AgentStatus":
        checks = data.get("checks", ())
        if isinstance(checks, list):
            checks_value = tuple(dict(item) for item in checks if isinstance(item, dict))
        elif isinstance(checks, tuple):
            checks_value = tuple(dict(item) for item in checks if isinstance(item, dict))
        else:
            raise ValueError("agent status checks must be a list")
        return cls(
            fingerprint=str(data["fingerprint"]),
            readiness=AgentReadiness(str(data.get("readiness", AgentReadiness.WARNING.value))),
            hostname=str(data.get("hostname", "")),
            version=str(data.get("version", "")),
            profile=str(data.get("profile", "")),
            site=str(data.get("site", "default")),
            cluster=None if data.get("cluster") is None else str(data.get("cluster")),
            message=str(data.get("message", "")),
            checks=checks_value,
        )


@dataclass(frozen=True)
class Agent:
    fingerprint: str
    hostname: str
    version: str
    profile: str
    site: str
    cluster: str | None = None
    status: AgentReadiness = AgentReadiness.WARNING
    labels: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Agent":
        labels = data.get("labels", {})
        if not isinstance(labels, dict):
            raise ValueError("agent labels must be a mapping")
        return cls(
            fingerprint=str(data["fingerprint"]),
            hostname=str(data.get("hostname", data["fingerprint"])),
            version=str(data.get("version", "")),
            profile=str(data.get("profile", "")),
            site=str(data.get("site", "default")),
            cluster=None if data.get("cluster") is None else str(data.get("cluster")),
            status=AgentReadiness(str(data.get("status", AgentReadiness.WARNING.value))),
            labels={str(k): str(v) for k, v in labels.items()},
        )


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
    agent_fingerprint: str | None = field(default=None, compare=False)
    trust_state: str = field(default="approved", compare=False)
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
    def from_dict(cls, data: dict[str, object]) -> "ManagedNode":
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
            agent_fingerprint=(
                None if node_data.get("agent_fingerprint") is None else str(node_data.pop("agent_fingerprint"))
            ),
            trust_state=str(node_data.pop("trust_state", "pending")),
            labels={str(key): str(value) for key, value in labels.items()},
        )
