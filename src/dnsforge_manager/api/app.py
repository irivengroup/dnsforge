from __future__ import annotations

from dataclasses import asdict
from typing import Any

from dnsforge_manager import __version__
from dnsforge_manager.core.boundaries import PRODUCT_BOUNDARIES
from dnsforge_manager.dnsbeat.service import DNSBeatService
from dnsforge_manager.inventory.models import ManagedNode, NodeRole, NodeStatus
from dnsforge_manager.inventory.service import NodeRegistrationService


class ManagerApplication:
    """Manager application core used by HTTP/CLI adapters.

    This layer coordinates inventory, DNSBeat and DNSSync without ever editing BIND files directly.
    """

    def __init__(
        self,
        registration_service: NodeRegistrationService | None = None,
        dnsbeat_service: DNSBeatService | None = None,
    ) -> None:
        self.registration_service = registration_service or NodeRegistrationService()
        self.dnsbeat_service = dnsbeat_service or DNSBeatService()

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "component": "dnsforge-manager", "version": __version__}

    def version(self) -> dict[str, Any]:
        return {"component": "dnsforge-manager", "version": __version__}

    def boundaries(self) -> dict[str, Any]:
        return {"products": [asdict(boundary) for boundary in PRODUCT_BOUNDARIES]}

    def nodes(self) -> dict[str, Any]:
        return {"nodes": [node.to_dict() for node in self.registration_service.list_nodes()]}

    def register_node(self, payload: dict[str, Any]) -> dict[str, Any]:
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
        return {"node": registered.to_dict(), "agent_token": registered.agent_token}

    def node(self, node_id: str) -> dict[str, Any]:
        return {"node": self.registration_service.get_node(node_id).to_dict()}

    def node_status(self, node_id: str) -> dict[str, Any]:
        node = self.registration_service.get_node(node_id)
        sample = self.dnsbeat_service.collect_node_health(node)
        return {
            "node_id": node.node_id,
            "status": node.status.value,
            "dnsbeat": asdict(sample),
        }

    def set_node_status(self, node_id: str, status: str) -> dict[str, Any]:
        node = self.registration_service.set_status(node_id, NodeStatus(status))
        return {"node": node.to_dict()}


def create_app(registration_service: NodeRegistrationService | None = None) -> ManagerApplication:
    """Return the framework-neutral Manager app core."""
    return ManagerApplication(registration_service=registration_service)
