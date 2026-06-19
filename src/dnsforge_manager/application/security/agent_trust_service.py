from __future__ import annotations

import hashlib
import secrets
from dataclasses import replace

from dnsforge_manager.domain.inventory.models import ManagedNode, NodeStatus
from dnsforge_manager.domain.security.models import AgentTrustState, NodeApprovalDecision
from dnsforge_manager.infrastructure.inventory.repository import NodeInventoryRepository


class AgentTrustService:
    """Trust model for Manager-to-DNSForge-agent relationships."""

    @staticmethod
    def fingerprint_for(endpoint: str, public_key: str = "") -> str:
        material = f"{endpoint}|{public_key}".encode("utf-8")
        return hashlib.sha256(material).hexdigest()

    def __init__(self, repository: NodeInventoryRepository) -> None:
        self.repository = repository

    def register_pending(self, node: ManagedNode, *, public_key: str = "") -> ManagedNode:
        fingerprint = node.agent_fingerprint or self.fingerprint_for(node.api_endpoint, public_key)
        pending = replace(
            node, agent_fingerprint=fingerprint, trust_state=AgentTrustState.PENDING.value, status=NodeStatus.REGISTERED
        )
        return self.repository.register(pending)

    def approve_node(self, node_id: str) -> NodeApprovalDecision:
        node = self.repository.get(node_id)
        fingerprint = node.agent_fingerprint or self.fingerprint_for(node.api_endpoint)
        approved = replace(
            node, agent_fingerprint=fingerprint, trust_state=AgentTrustState.APPROVED.value, status=NodeStatus.ACTIVE
        )
        self.repository.upsert(approved)
        return NodeApprovalDecision(node_id=node_id, approved=True, fingerprint=fingerprint, message="approved")

    def revoke_node(self, node_id: str) -> ManagedNode:
        node = self.repository.get(node_id)
        revoked = replace(node, trust_state=AgentTrustState.REVOKED.value, status=NodeStatus.DISABLED, agent_token=None)
        return self.repository.upsert(revoked)

    def rotate_token(self, node_id: str) -> ManagedNode:
        node = self.repository.get(node_id)
        if node.trust_state == AgentTrustState.REVOKED.value:
            raise ValueError(f"cannot rotate token for revoked node: {node_id}")
        return self.repository.upsert(replace(node, agent_token=secrets.token_urlsafe(32)))

    @staticmethod
    def assert_trusted(node: ManagedNode) -> None:
        if node.trust_state != AgentTrustState.APPROVED.value:
            raise PermissionError(f"node is not approved for Manager operations: {node.node_id}")
        if node.status in {NodeStatus.DISABLED, NodeStatus.UNREACHABLE}:
            raise PermissionError(f"node is not active for Manager operations: {node.node_id}")
