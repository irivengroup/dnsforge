from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from dnsforge_manager.domain.inventory.models import ManagedNode, NodeStatus
from dnsforge_manager.infrastructure.persistence import JsonDocumentStore


class NodeInventoryRepository:
    def register(self, node: ManagedNode) -> ManagedNode:
        raise NotImplementedError

    def upsert(self, node: ManagedNode) -> ManagedNode:
        raise NotImplementedError

    def get(self, node_id: str) -> ManagedNode:
        raise NotImplementedError

    def list(self) -> tuple[ManagedNode, ...]:
        raise NotImplementedError

    def set_status(self, node_id: str, status: NodeStatus) -> ManagedNode:
        node = replace(self.get(node_id), status=status)
        return self.upsert(node)


class InMemoryNodeInventoryRepository(NodeInventoryRepository):
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


class JsonNodeInventoryRepository(NodeInventoryRepository):
    """JSON inventory backend retained as the Manager default persistence adapter."""

    def __init__(self, path: Path) -> None:
        self.store = JsonDocumentStore(path)

    def _read(self) -> dict[str, ManagedNode]:
        return self.store.read_items("nodes", ManagedNode.from_dict)

    def _write(self, nodes: dict[str, ManagedNode]) -> None:
        self.store.write_items(
            "nodes",
            (node.to_dict(include_token=True) for node in sorted(nodes.values(), key=lambda item: item.node_id)),
        )

    def register(self, node: ManagedNode) -> ManagedNode:
        nodes = self._read()
        if node.node_id in nodes:
            raise ValueError(f"node already registered: {node.node_id}")
        nodes[node.node_id] = node
        self._write(nodes)
        return node

    def upsert(self, node: ManagedNode) -> ManagedNode:
        nodes = self._read()
        nodes[node.node_id] = node
        self._write(nodes)
        return node

    def get(self, node_id: str) -> ManagedNode:
        nodes = self._read()
        try:
            return nodes[node_id]
        except KeyError as exc:
            raise KeyError(f"unknown node: {node_id}") from exc

    def list(self) -> tuple[ManagedNode, ...]:
        return tuple(sorted(self._read().values(), key=lambda item: item.node_id))
