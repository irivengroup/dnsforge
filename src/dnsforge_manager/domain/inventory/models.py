from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


def _int_value(value: object, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value)
    return default


class NodeRole(str, Enum):
    AUTHORITATIVE = "authoritative"
    PROXY_FORWARDER = "proxy-forwarder"
    PROXY_HYBRID = "proxy-hybrid"
    CATALOG_PUBLISHER = "catalog-publisher"
    CATALOG_SUBSCRIBER = "catalog-subscriber"
    HIDDEN_MASTER = "hidden-master"
    STEALTH_SECONDARY = "stealth-secondary"


@dataclass(frozen=True)
class InventoryRole:
    role_id: str
    name: str
    description: str
    bind_capabilities: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


INVENTORY_ROLES: tuple[InventoryRole, ...] = (
    InventoryRole(
        role_id=NodeRole.AUTHORITATIVE.value,
        name="Authoritative",
        description="Authoritative BIND node serving master or slave zones.",
        bind_capabilities=("zones", "dnssec", "catalog-consume"),
    ),
    InventoryRole(
        role_id=NodeRole.PROXY_FORWARDER.value,
        name="Proxy Forwarder",
        description="Forwarding proxy node for recursive or upstream forwarding flows.",
        bind_capabilities=("forwarding", "views", "acl"),
    ),
    InventoryRole(
        role_id=NodeRole.PROXY_HYBRID.value,
        name="Proxy Hybrid",
        description="Hybrid proxy node combining forwarding and selected authoritative zones.",
        bind_capabilities=("forwarding", "zones", "views", "acl"),
    ),
    InventoryRole(
        role_id=NodeRole.CATALOG_PUBLISHER.value,
        name="Catalog Publisher",
        description="Node publishing BIND catalog zones for member synchronization.",
        bind_capabilities=("catalog-publish", "zones"),
    ),
    InventoryRole(
        role_id=NodeRole.CATALOG_SUBSCRIBER.value,
        name="Catalog Subscriber",
        description="Node subscribing to catalog zones and materializing member zones.",
        bind_capabilities=("catalog-consume", "zones"),
    ),
    InventoryRole(
        role_id=NodeRole.HIDDEN_MASTER.value,
        name="Hidden Master",
        description="Non-public authoritative source node for protected zone transfers.",
        bind_capabilities=("zones", "dnssec", "transfer-source"),
    ),
    InventoryRole(
        role_id=NodeRole.STEALTH_SECONDARY.value,
        name="Stealth Secondary",
        description="Secondary authoritative node not directly advertised to clients.",
        bind_capabilities=("zones", "transfer-target", "catalog-consume"),
    ),
)


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


class ConfigurationComplianceState(str, Enum):
    COMPLIANT = "COMPLIANT"
    WARNING = "WARNING"
    DRIFTED = "DRIFTED"
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
class AgentComplianceStatus:
    fingerprint: str
    compliance: ConfigurationComplianceState
    drift_count: int = 0
    last_checked: str = ""
    message: str = ""
    findings: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["compliance"] = self.compliance.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "AgentComplianceStatus":
        findings = data.get("findings", ())
        if isinstance(findings, list):
            findings_value = tuple(dict(item) for item in findings if isinstance(item, dict))
        elif isinstance(findings, tuple):
            findings_value = tuple(dict(item) for item in findings if isinstance(item, dict))
        else:
            raise ValueError("agent compliance findings must be a list")
        return cls(
            fingerprint=str(data["fingerprint"]),
            compliance=ConfigurationComplianceState(
                str(data.get("compliance", ConfigurationComplianceState.WARNING.value))
            ),
            drift_count=_int_value(data.get("drift_count", 0)),
            last_checked=str(data.get("last_checked", "")),
            message=str(data.get("message", "")),
            findings=findings_value,
        )


@dataclass(frozen=True)
class AgentComplianceEvent:
    event_id: str
    fingerprint: str
    compliance: ConfigurationComplianceState
    drift_count: int = 0
    observed_at: str = ""
    previous_compliance: ConfigurationComplianceState | None = None
    previous_drift_count: int | None = None
    message: str = ""
    transition: bool = False

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["compliance"] = self.compliance.value
        if self.previous_compliance is not None:
            data["previous_compliance"] = self.previous_compliance.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "AgentComplianceEvent":
        previous = data.get("previous_compliance")
        return cls(
            event_id=str(data["event_id"]),
            fingerprint=str(data["fingerprint"]),
            compliance=ConfigurationComplianceState(
                str(data.get("compliance", ConfigurationComplianceState.WARNING.value))
            ),
            drift_count=_int_value(data.get("drift_count", 0)),
            observed_at=str(data.get("observed_at", "")),
            previous_compliance=None if previous in (None, "") else ConfigurationComplianceState(str(previous)),
            previous_drift_count=(
                None if data.get("previous_drift_count") is None else _int_value(data.get("previous_drift_count", 0))
            ),
            message=str(data.get("message", "")),
            transition=bool(data.get("transition", False)),
        )


@dataclass(frozen=True)
class AgentComplianceTrend:
    fingerprint: str
    current_compliance: ConfigurationComplianceState
    observations: int = 0
    transitions: int = 0
    drift_observations: int = 0
    total_drift_count: int = 0
    first_observed_at: str = ""
    last_observed_at: str = ""
    last_transition_at: str = ""
    recurrent_drift: bool = False

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["current_compliance"] = self.current_compliance.value
        return data


@dataclass(frozen=True)
class Agent:
    fingerprint: str
    hostname: str
    version: str
    profile: str
    role: NodeRole = NodeRole.AUTHORITATIVE
    site: str = "default"
    cluster: str | None = None
    status: AgentReadiness = AgentReadiness.WARNING
    labels: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["role"] = self.role.value
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
            role=NodeRole(str(data.get("role", _role_from_profile(str(data.get("profile", ""))).value))),
            site=str(data.get("site", "default")),
            cluster=None if data.get("cluster") is None else str(data.get("cluster")),
            status=AgentReadiness(str(data.get("status", AgentReadiness.WARNING.value))),
            labels={str(k): str(v) for k, v in labels.items()},
        )


def _role_from_profile(profile: str) -> NodeRole:
    normalized = profile.strip().lower()
    if normalized in {role.value for role in NodeRole}:
        return NodeRole(normalized)
    if normalized == "proxy":
        return NodeRole.PROXY_HYBRID
    return NodeRole.AUTHORITATIVE


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
