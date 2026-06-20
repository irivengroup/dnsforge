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
from dnsforge_manager.application.inventory.central_inventory_service import CentralInventoryService
from dnsforge_manager.infrastructure.inventory.central_repository import CentralInventoryRepository
from dnsforge_manager.application.rbac.rbac_service import RbacService
from dnsforge_manager.application.workflows.change_workflow import ManagerChangeWorkflow
from dnsforge_manager.domain.workflows.models import ManagerChangeRequest
from dnsforge_manager.infrastructure.dnssync.client import (
    DNSForgeNodeClient,
    RecordingDNSForgeNodeClient,
)


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
        change_workflow: ManagerChangeWorkflow | None = None,
        node_client: DNSForgeNodeClient | None = None,
        central_inventory: CentralInventoryService | None = None,
        central_inventory_repository: CentralInventoryRepository | None = None,
    ) -> None:
        self.registration_service = registration_service or NodeRegistrationService()
        self.dnsbeat_service = dnsbeat_service or DNSBeatService()
        self.rbac_service = rbac_service or RbacService()
        self.audit_repository = audit_repository or ManagerAuditRepository()
        self.change_workflow = change_workflow or ManagerChangeWorkflow(dnsbeat_service=self.dnsbeat_service)
        self.node_client = node_client or RecordingDNSForgeNodeClient()
        self.central_inventory = central_inventory or CentralInventoryService(central_inventory_repository)

    def _require(self, role: str, permission: str) -> None:
        self.rbac_service.require(role, permission)

    def _audit(
        self,
        *,
        actor: str,
        action: str,
        target: str,
        result: str,
        metadata: dict[str, object] | None = None,
    ) -> None:
        self.audit_repository.append(
            ManagerAuditEvent(
                actor=actor,
                action=action,
                target=target,
                result=result,
                metadata=metadata or {},
            )
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

    def register_node(
        self,
        payload: dict[str, Any],
        *,
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
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
        self._audit(
            actor=actor,
            action="node.register",
            target=registered.node_id,
            result="pending",
        )
        return {"node": registered.to_dict(), "agent_token": registered.agent_token}

    def approve_node(
        self,
        node_id: str,
        *,
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:trust:admin")
        decision = self.registration_service.approve_node(node_id)
        self._audit(actor=actor, action="node.approve", target=node_id, result="approved")
        return {"decision": asdict(decision)}

    def revoke_node(
        self,
        node_id: str,
        *,
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:trust:admin")
        node = self.registration_service.revoke_node(node_id)
        self._audit(actor=actor, action="node.revoke", target=node_id, result="revoked")
        return {"node": node.to_dict()}

    def rotate_node_token(
        self,
        node_id: str,
        *,
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:trust:admin")
        node = self.registration_service.rotate_token(node_id)
        self._audit(actor=actor, action="node.token.rotate", target=node_id, result="rotated")
        return {"node": node.to_dict(), "agent_token": node.agent_token}

    def node(self, node_id: str, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:nodes:read")
        return {"node": self.registration_service.get_node(node_id).to_dict()}

    def _agent_readiness(self, node_id: str) -> dict[str, object]:
        readiness = getattr(self.node_client, "readiness", None)
        if callable(readiness):
            value = readiness(node_id)
            if isinstance(value, dict):
                return value
        return {
            "node_id": node_id,
            "status": "WARNING",
            "score": 50,
            "checks": [
                {
                    "name": "Agent Readiness",
                    "status": "WARNING",
                    "message": "node client does not expose readiness",
                    "critical": False,
                }
            ],
        }

    def node_status(self, node_id: str, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:dnsbeat:read")
        node = self.registration_service.get_node(node_id)
        sample = self.dnsbeat_service.collect_node_health(node)
        return {
            "node_id": node.node_id,
            "status": node.status.value,
            "dnsbeat": asdict(sample),
            "readiness": self._agent_readiness(node.node_id),
        }

    def node_readiness(self, node_id: str, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:dnsbeat:read")
        node = self.registration_service.get_node(node_id)
        return {"node_id": node.node_id, "readiness": self._agent_readiness(node.node_id)}

    def set_node_status(
        self, node_id: str, status: str, *, actor: str = "system", role: str = "operator"
    ) -> dict[str, Any]:
        self._require(role, "manager:nodes:operate")
        node = self.registration_service.set_status(node_id, NodeStatus(status))
        self._audit(actor=actor, action="node.status", target=node_id, result=status)
        return {"node": node.to_dict()}

    def changes(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:changes:read")
        return {"changes": [change.to_dict() for change in self.change_workflow.list_changes()]}

    def create_change(
        self,
        payload: dict[str, Any],
        *,
        actor: str = "system",
        role: str = "operator",
    ) -> dict[str, Any]:
        self._require(role, "manager:changes:operate")
        change = ManagerChangeRequest(
            cluster_id=str(payload["cluster_id"]),
            operation=str(payload["operation"]),
            payload=dict(payload.get("payload", {})),
            created_by=actor,
        )
        created = self.change_workflow.create_change(change)
        self._audit(
            actor=actor,
            action="change.create",
            target=created.change_id,
            result=created.status.value,
        )
        return {"change": created.to_dict()}

    def change(self, change_id: str, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:changes:read")
        return {"change": self.change_workflow.get_change(change_id).to_dict()}

    def dry_run_change(
        self,
        change_id: str,
        *,
        actor: str = "system",
        role: str = "operator",
    ) -> dict[str, Any]:
        self._require(role, "manager:changes:operate")
        execution = self.change_workflow.dry_run_change(
            change_id,
            self.registration_service.list_nodes(),
        )
        self._audit(
            actor=actor,
            action="change.dry_run",
            target=change_id,
            result="accepted" if execution.accepted else "failed",
            metadata={"plan_hash": execution.plan_hash},
        )
        return {
            "execution": {
                "cluster_id": execution.cluster_id,
                "mode": execution.mode.value,
                "plan_hash": execution.plan_hash,
                "accepted": execution.accepted,
                "results": [result.__dict__ for result in execution.results],
            }
        }

    def approve_change(
        self,
        change_id: str,
        *,
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:changes:admin")
        change = self.change_workflow.approve_change(change_id, actor=actor)
        self._audit(
            actor=actor,
            action="change.approve",
            target=change_id,
            result=change.status.value,
        )
        return {"change": change.to_dict()}

    def reject_change(
        self,
        change_id: str,
        *,
        reason: str | None = None,
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:changes:admin")
        change = self.change_workflow.reject_change(change_id, reason=reason)
        self._audit(
            actor=actor,
            action="change.reject",
            target=change_id,
            result=change.status.value,
        )
        return {"change": change.to_dict()}

    def apply_change(
        self,
        change_id: str,
        *,
        approved_plan_hash: str | None = None,
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:changes:admin")
        execution = self.change_workflow.apply_change(
            change_id,
            self.registration_service.list_nodes(),
            self.node_client,
            approved_plan_hash=approved_plan_hash,
        )
        self._audit(
            actor=actor,
            action="change.apply",
            target=change_id,
            result="accepted" if execution.accepted else "failed",
            metadata={"plan_hash": execution.plan_hash},
        )
        return {"change": self.change_workflow.get_change(change_id).to_dict()}

    def rollback_change(
        self,
        change_id: str,
        *,
        approved_plan_hash: str | None = None,
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:changes:admin")
        execution = self.change_workflow.rollback_change(
            change_id,
            self.registration_service.list_nodes(),
            self.node_client,
            approved_plan_hash=approved_plan_hash,
        )
        self._audit(
            actor=actor,
            action="change.rollback",
            target=change_id,
            result="accepted" if execution.accepted else "failed",
            metadata={"plan_hash": execution.plan_hash},
        )
        return {"change": self.change_workflow.get_change(change_id).to_dict()}

    def inventory_sites(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:inventory:read")
        return {"sites": [site.to_dict() for site in self.central_inventory.list_sites()]}

    def create_inventory_site(
        self,
        payload: dict[str, Any],
        *,
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:inventory:write")
        site = self.central_inventory.create_site(payload)
        self._audit(
            actor=actor,
            action="inventory.site.create",
            target=site.site_id,
            result="created",
        )
        return {"site": site.to_dict()}

    def inventory_clusters(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:inventory:read")
        return {"clusters": [cluster.to_dict() for cluster in self.central_inventory.list_clusters()]}

    def create_inventory_cluster(
        self,
        payload: dict[str, Any],
        *,
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:inventory:write")
        cluster = self.central_inventory.create_cluster(payload)
        self._audit(
            actor=actor,
            action="inventory.cluster.create",
            target=cluster.cluster_id,
            result="created",
        )
        return {"cluster": cluster.to_dict()}

    def inventory_agents(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:inventory:read")
        return {"agents": [agent.to_dict() for agent in self.central_inventory.list_agents()]}

    def register_inventory_agent(
        self,
        payload: dict[str, Any],
        *,
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:inventory:write")
        agent = self.central_inventory.register_agent(payload)
        self._audit(
            actor=actor,
            action="inventory.agent.register",
            target=agent.fingerprint,
            result=agent.status.value,
        )
        return {"agent": agent.to_dict()}

    def inventory_environments(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:inventory:read")
        return {"environments": [environment.to_dict() for environment in self.central_inventory.list_environments()]}

    def inventory_agent_status(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:inventory:read")
        return self.central_inventory.aggregate_readiness()

    def update_inventory_agent_status(
        self,
        payload: dict[str, Any],
        *,
        actor: str = "system",
        role: str = "operator",
    ) -> dict[str, Any]:
        self._require(role, "manager:inventory:write")
        status = self.central_inventory.update_agent_status(payload)
        self._audit(
            actor=actor,
            action="inventory.agent.status",
            target=status.fingerprint,
            result=status.readiness.value,
        )
        return {"agent_status": status.to_dict()}

    def audit_events(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:audit:read")
        return {"events": [event.to_dict() for event in self.audit_repository.list()]}


def create_app(
    registration_service: NodeRegistrationService | None = None,
    central_inventory_repository: CentralInventoryRepository | None = None,
) -> ManagerApplication:
    """Return the framework-neutral Manager app core."""
    return ManagerApplication(
        registration_service=registration_service,
        central_inventory_repository=central_inventory_repository,
    )
