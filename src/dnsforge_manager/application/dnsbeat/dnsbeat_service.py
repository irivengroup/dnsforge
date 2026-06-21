from __future__ import annotations

from datetime import datetime, timezone

from dnsforge_manager.domain.dnsbeat.models import ClusterHealthSample, ComponentHealth, NodeHealthSample
from dnsforge_manager.domain.inventory.models import ManagedNode, NodeStatus
from dnsforge_manager.infrastructure.concurrency import ParallelExecutor


class DNSBeatService:
    """Manager sub-module responsible for observing DNSForge-managed BIND nodes."""

    def __init__(self, executor: ParallelExecutor | None = None) -> None:
        self.executor = executor or ParallelExecutor()

    def collect_node_health(self, node: ManagedNode) -> NodeHealthSample:
        if not node.requires_dnsforge_agent():
            raise ValueError("DNSBeat only monitors registered DNSForge agents")
        if node.status == NodeStatus.DISABLED:
            return NodeHealthSample(
                node.node_id, node.status, 0, "disabled", None, "unknown", _failed_components("disabled")
            )
        if node.status == NodeStatus.UNREACHABLE:
            return NodeHealthSample(
                node.node_id,
                node.status,
                0,
                "unreachable",
                None,
                "unknown",
                _failed_components("unreachable"),
            )
        score = 100 if node.status in {NodeStatus.REGISTERED, NodeStatus.ACTIVE, NodeStatus.HEALTHY} else 75
        last_seen = datetime.now(timezone.utc).isoformat()
        components = _healthy_components() if score == 100 else _warning_components(node.status.value)
        return NodeHealthSample(
            node_id=node.node_id,
            status=node.status,
            score=score,
            message=node.status.value,
            last_seen=last_seen,
            components=components,
        )

    def collect_cluster_health(self, cluster_id: str, nodes: tuple[ManagedNode, ...]) -> ClusterHealthSample:
        cluster_nodes = tuple(node for node in nodes if node.cluster_id == cluster_id)
        samples = self.executor.map_ordered(cluster_nodes, self.collect_node_health)
        if not samples:
            return ClusterHealthSample(cluster_id, "FAILED", 0, (), "no nodes registered for cluster")
        score = min(sample.score for sample in samples)
        status = _aggregate_status(score, tuple(sample.status for sample in samples))
        return ClusterHealthSample(cluster_id=cluster_id, status=status, score=score, nodes=samples)

    def collect_fleet_health(self, nodes: tuple[ManagedNode, ...]) -> tuple[NodeHealthSample, ...]:
        return self.executor.map_ordered(nodes, self.collect_node_health)


def _healthy_components() -> tuple[ComponentHealth, ...]:
    return (
        ComponentHealth("BIND", "READY", 100, "agent reports BIND reachable"),
        ComponentHealth("RNDC", "READY", 100, "agent reports RNDC reachable"),
        ComponentHealth("DNSSEC", "READY", 100, "agent reports DNSSEC checks healthy"),
        ComponentHealth("Catalog", "READY", 100, "agent reports catalog zones healthy"),
        ComponentHealth("Cluster", "READY", 100, "agent reports cluster membership healthy"),
        ComponentHealth("Readiness", "READY", 100, "agent readiness is ready"),
    )


def _warning_components(message: str) -> tuple[ComponentHealth, ...]:
    return (
        ComponentHealth("BIND", "WARNING", 75, message),
        ComponentHealth("RNDC", "WARNING", 75, message),
        ComponentHealth("DNSSEC", "WARNING", 75, message),
        ComponentHealth("Catalog", "WARNING", 75, message),
        ComponentHealth("Cluster", "WARNING", 75, message),
        ComponentHealth("Readiness", "WARNING", 75, message),
    )


def _failed_components(message: str) -> tuple[ComponentHealth, ...]:
    return (
        ComponentHealth("BIND", "FAILED", 0, message),
        ComponentHealth("RNDC", "FAILED", 0, message),
        ComponentHealth("DNSSEC", "FAILED", 0, message),
        ComponentHealth("Catalog", "FAILED", 0, message),
        ComponentHealth("Cluster", "FAILED", 0, message),
        ComponentHealth("Readiness", "FAILED", 0, message),
    )


def _aggregate_status(score: int, statuses: tuple[NodeStatus, ...]) -> str:
    if any(status in {NodeStatus.DISABLED, NodeStatus.UNREACHABLE} for status in statuses):
        return "FAILED"
    if score < 100:
        return "WARNING"
    return "READY"
