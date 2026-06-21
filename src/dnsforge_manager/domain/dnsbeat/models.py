from __future__ import annotations

from dataclasses import asdict, dataclass

from dnsforge_manager.domain.inventory.models import NodeStatus


@dataclass(frozen=True)
class ComponentHealth:
    component: str
    status: str
    score: int
    message: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class NodeHealthSample:
    node_id: str
    status: NodeStatus
    score: int
    message: str
    last_seen: str | None = None
    drift_status: str = "unknown"
    components: tuple[ComponentHealth, ...] = ()

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        data["components"] = [component.to_dict() for component in self.components]
        return data


@dataclass(frozen=True)
class ClusterHealthSample:
    cluster_id: str
    status: str
    score: int
    nodes: tuple[NodeHealthSample, ...]
    message: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "cluster_id": self.cluster_id,
            "status": self.status,
            "score": self.score,
            "message": self.message,
            "nodes": [node.to_dict() for node in self.nodes],
        }
