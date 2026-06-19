from __future__ import annotations

from dnsforge_manager.inventory.models import ManagedNode
from dnsforge_manager.inventory.repository import NodeInventoryRepository


class NodeRegistrationService:
    def __init__(self, repository: NodeInventoryRepository | None = None) -> None:
        self.repository = repository or NodeInventoryRepository()

    def register_node(self, node: ManagedNode) -> ManagedNode:
        if not node.api_endpoint.startswith(("https://", "http://")):
            raise ValueError("node api_endpoint must be an HTTP(S) DNSForge API endpoint")
        return self.repository.register(node)

    def list_nodes(self) -> tuple[ManagedNode, ...]:
        return self.repository.list()
