from __future__ import annotations

from dataclasses import replace

from dnsforge_manager.inventory.models import ManagedNode, NodeStatus


class NodeInventoryRepository:
    def __init__(self) -> None:
        self._nodes: dict[str, ManagedNode] = {}

    def register(self, node: ManagedNode) -> ManagedNode:
        if node.node_id in self._nodes:
            raise ValueError(f"node already registered: {node.node_id}")
        self._nodes[node.node_id] = node
        return node

    def upsert(self, node: ManagedNode) -> ManagedNode:
        self._nodes[node.node_id] = node
        return node

    def get(self, node_id: str) -> ManagedNode:
        try:
            return self._nodes[node_id]
        except KeyError as exc:
            raise KeyError(f"unknown node: {node_id}") from exc

    def list(self) -> tuple[ManagedNode, ...]:
        return tuple(sorted(self._nodes.values(), key=lambda item: item.node_id))

    def set_status(self, node_id: str, status: NodeStatus) -> ManagedNode:
        node = replace(self.get(node_id), status=status)
        self._nodes[node_id] = node
        return node
