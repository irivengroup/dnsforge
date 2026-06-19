from __future__ import annotations

from dataclasses import dataclass

from dnsforge_manager.inventory.models import ManagedNode, NodeStatus


@dataclass(frozen=True)
class NodeHealthSample:
    node_id: str
    status: NodeStatus
    score: int
    message: str


class DNSBeatService:
    """Manager sub-module responsible for observing DNSForge-managed nodes."""

    def collect_node_health(self, node: ManagedNode) -> NodeHealthSample:
        if not node.requires_dnsforge_agent():
            raise ValueError("DNSBeat only monitors registered DNSForge agents")
        return NodeHealthSample(node_id=node.node_id, status=node.status, score=100, message="registered")
