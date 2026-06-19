from __future__ import annotations

from dataclasses import asdict
from typing import Any

from dnsforge_manager import __version__
from dnsforge_manager.domain.audit.models import ManagerAuditEvent
from dnsforge_manager.infrastructure.audit.repository import ManagerAuditRepository
from dnsforge_manager.domain.core.boundaries import PRODUCT_BOUNDARIES
from dnsforge_manager.application.dnsbeat.dnsbeat_service import DNSBeatService
from dnsforge_manager.domain.inventory.models import ManagedNode, NodeRole, NodeStatus
from dnsforge_manager.application.inventory.node_registration_service import NodeRegistrationService
from dnsforge_manager.application.rbac.rbac_service import RbacService


class ManagerApplication:
    """Manager application core used by HTTP/CLI adapters.

    This layer coordinates inventory, DNSBeat and DNSSync without ever editing BIND files directly.
    """

    def __init__(
        self,
        registration_service: NodeRegistrationService | None = None,
        dnsbeat_service: DNSBeatService | None = None,
        rbac_service: RbacService | None = None,
        audit_repository: ManagerAuditRepository | None = None,
    ) -> None:
        self.registration_service = registration_service or NodeRegistrationService()
        self.dnsbeat_service = dnsbeat_service or DNSBeatService()
        self.rbac_service = rbac_service or RbacService()
        self.audit_repository = audit_repository or ManagerAuditRepository()

    def _require(self, role: str, permission: str) -> None:
        self.rbac_service.require(role, permission)

    def _audit(
        self, *, actor: str, action: str, target: str, result: str, metadata: dict[str, object] | None = None
    ) -> None:
        self.audit_repository.append(
            ManagerAuditEvent(actor=actor, action=action, target=target, result=result, metadata=metadata or {})
        )

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "component": "dnsforge-manager", "version": __version__}

    def version(self) -> dict[str, Any]:
        return {"component": "dnsforge-manager", "version": __version__}

    def boundaries(self) -> dict[str, Any]:
        return {"products": [asdict(boundary) for boundary in PRODUCT_BOUNDARIES]}

    def nodes(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:nodes:read")
        return {"nodes": [node.to_dict() for node in self.registration_service.list_nodes()]}

    def register_node(self, payload: dict[str, Any], *, actor: str = "system", role: str = "admin") -> dict[str, Any]:
        self._require(role, "manager:trust:admin")
        node = ManagedNode(
            node_id=str(payload["node_id"]),
            name=str(payload.get("name", payload["node_id"])),
            api_endpoint=str(payload["api_endpoint"]),
            role=NodeRole(str(payload["role"])),
            site=str(payload.get("site", "default")),
            environment=str(payload.get("environment", "production")),
            cluster_id=None if payload.get("cluster_id") is None else str(payload["cluster_id"]),
            labels={str(key): str(value) for key, value in dict(payload.get("labels", {})).items()},
        )
        registered = self.registration_service.register_node(node)
        self._audit(actor=actor, action="node.register", target=registered.node_id, result="pending")
        return {"node": registered.to_dict(), "agent_token": registered.agent_token}

    def approve_node(self, node_id: str, *, actor: str = "system", role: str = "admin") -> dict[str, Any]:
        self._require(role, "manager:trust:admin")
        decision = self.registration_service.approve_node(node_id)
        self._audit(actor=actor, action="node.approve", target=node_id, result="approved")
        return {"decision": asdict(decision)}

    def revoke_node(self, node_id: str, *, actor: str = "system", role: str = "admin") -> dict[str, Any]:
        self._require(role, "manager:trust:admin")
        node = self.registration_service.revoke_node(node_id)
        self._audit(actor=actor, action="node.revoke", target=node_id, result="revoked")
        return {"node": node.to_dict()}

    def rotate_node_token(self, node_id: str, *, actor: str = "system", role: str = "admin") -> dict[str, Any]:
        self._require(role, "manager:trust:admin")
        node = self.registration_service.rotate_token(node_id)
        self._audit(actor=actor, action="node.token.rotate", target=node_id, result="rotated")
        return {"node": node.to_dict(), "agent_token": node.agent_token}

    def node(self, node_id: str, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:nodes:read")
        return {"node": self.registration_service.get_node(node_id).to_dict()}

    def node_status(self, node_id: str, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:dnsbeat:read")
        node = self.registration_service.get_node(node_id)
        sample = self.dnsbeat_service.collect_node_health(node)
        return {
            "node_id": node.node_id,
            "status": node.status.value,
            "dnsbeat": asdict(sample),
        }

    def set_node_status(
        self, node_id: str, status: str, *, actor: str = "system", role: str = "operator"
    ) -> dict[str, Any]:
        self._require(role, "manager:nodes:operate")
        node = self.registration_service.set_status(node_id, NodeStatus(status))
        self._audit(actor=actor, action="node.status", target=node_id, result=status)
        return {"node": node.to_dict()}

    def audit_events(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:audit:read")
        return {"events": [event.to_dict() for event in self.audit_repository.list()]}


def create_app(registration_service: NodeRegistrationService | None = None) -> ManagerApplication:
    """Return the framework-neutral Manager app core."""
    return ManagerApplication(registration_service=registration_service)
