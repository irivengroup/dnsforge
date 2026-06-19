from __future__ import annotations

from dataclasses import dataclass

from dnsforge_manager.domain.inventory.models import NodeStatus


@dataclass(frozen=True)
class NodeHealthSample:
    node_id: str
    status: NodeStatus
    score: int
    message: str
    last_seen: str | None = None
    drift_status: str = "unknown"
