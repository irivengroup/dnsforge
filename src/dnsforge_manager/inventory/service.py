from __future__ import annotations

import secrets
from dataclasses import replace

from dnsforge_manager.inventory.models import ManagedNode, NodeStatus
from dnsforge_manager.inventory.repository import InMemoryNodeInventoryRepository, NodeInventoryRepository


class NodeRegistrationService:
    def __init__(self, repository: NodeInventoryRepository | None = None) -> None:
        self.repository = repository or InMemoryNodeInventoryRepository()

    def register_node(self, node: ManagedNode) -> ManagedNode:
        if not node.api_endpoint.startswith(("https://", "http://")):
            raise ValueError("node api_endpoint must be an HTTP(S) DNSForge API endpoint")
        token = node.agent_token or secrets.token_urlsafe(32)
        return self.repository.register(replace(node, agent_token=token, status=NodeStatus.REGISTERED))

    def get_node(self, node_id: str) -> ManagedNode:
        return self.repository.get(node_id)

    def list_nodes(self) -> tuple[ManagedNode, ...]:
        return self.repository.list()

    def set_status(self, node_id: str, status: NodeStatus) -> ManagedNode:
        return self.repository.set_status(node_id, status)

    def activate_node(self, node_id: str) -> ManagedNode:
        return self.set_status(node_id, NodeStatus.ACTIVE)

    def disable_node(self, node_id: str) -> ManagedNode:
        return self.set_status(node_id, NodeStatus.DISABLED)
