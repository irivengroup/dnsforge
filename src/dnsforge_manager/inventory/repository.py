from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from dnsforge_manager.inventory.models import ManagedNode, NodeStatus


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
    """Small JSON inventory backend; production storage can later be PostgreSQL behind this same port."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> dict[str, ManagedNode]:
        if not self.path.exists():
            return {}
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("manager node inventory must be a JSON object")
        nodes = raw.get("nodes", [])
        if not isinstance(nodes, list):
            raise ValueError("manager node inventory 'nodes' must be a list")
        return {node.node_id: node for node in (ManagedNode.from_dict(item) for item in nodes)}

    def _write(self, nodes: dict[str, ManagedNode]) -> None:
        payload = {"nodes": [node.to_dict(include_token=True) for node in sorted(nodes.values(), key=lambda item: item.node_id)]}
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(self.path)

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
