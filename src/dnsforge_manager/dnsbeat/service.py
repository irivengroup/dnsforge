from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from dnsforge_manager.inventory.models import ManagedNode, NodeStatus


@dataclass(frozen=True)
class NodeHealthSample:
    node_id: str
    status: NodeStatus
    score: int
    message: str
    last_seen: str | None = None
    drift_status: str = "unknown"


class DNSBeatService:
    """Manager sub-module responsible for observing DNSForge-managed nodes."""

    def collect_node_health(self, node: ManagedNode) -> NodeHealthSample:
        if not node.requires_dnsforge_agent():
            raise ValueError("DNSBeat only monitors registered DNSForge agents")
        if node.status == NodeStatus.DISABLED:
            return NodeHealthSample(node.node_id, node.status, 0, "disabled", None, "unknown")
        if node.status == NodeStatus.UNREACHABLE:
            return NodeHealthSample(node.node_id, node.status, 0, "unreachable", None, "unknown")
        score = 100 if node.status in {NodeStatus.REGISTERED, NodeStatus.ACTIVE, NodeStatus.HEALTHY} else 75
        last_seen = datetime.now(timezone.utc).isoformat()
        return NodeHealthSample(node_id=node.node_id, status=node.status, score=score, message=node.status.value, last_seen=last_seen)
