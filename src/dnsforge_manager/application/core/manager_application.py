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
from dnsforge_manager.application.security.agent_trust_service import AgentTrustService
from dnsforge_manager.application.dnssync.dnssync_service import DNSSyncService
from dnsforge_manager.domain.dnssync.models import DNSForgeOperation, SyncExecution, SyncMode, SyncPlan
from dnsforge_manager.infrastructure.inventory.central_repository import CentralInventoryRepository
from dnsforge_manager.application.rbac.rbac_service import RbacService
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
        dnssync_service: DNSSyncService | None = None,
        node_client: DNSForgeNodeClient | None = None,
        central_inventory: CentralInventoryService | None = None,
        central_inventory_repository: CentralInventoryRepository | None = None,
        agent_trust_service: AgentTrustService | None = None,
    ) -> None:
        self.registration_service = registration_service or NodeRegistrationService()
        self.dnsbeat_service = dnsbeat_service or DNSBeatService()
        self.rbac_service = rbac_service or RbacService()
        self.audit_repository = audit_repository or ManagerAuditRepository()
        self.dnssync_service = dnssync_service or DNSSyncService()
        self.node_client = node_client or RecordingDNSForgeNodeClient()
        self._dnssync_plans: dict[str, SyncPlan] = {}
        self._dnssync_executions: list[SyncExecution] = []
        self.central_inventory = central_inventory or CentralInventoryService(central_inventory_repository)
        self.agent_trust_service = agent_trust_service or AgentTrustService()

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
            "dnsbeat": sample.to_dict(),
            "readiness": self._agent_readiness(node.node_id),
        }

    def node_readiness(self, node_id: str, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:dnsbeat:read")
        node = self.registration_service.get_node(node_id)
        return {"node_id": node.node_id, "readiness": self._agent_readiness(node.node_id)}

    def monitor_status(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:dnsbeat:read")
        samples = self.dnsbeat_service.collect_fleet_health(self.registration_service.list_nodes())
        status = "READY"
        if any(sample.score == 0 for sample in samples):
            status = "FAILED"
        elif any(sample.score < 100 for sample in samples):
            status = "WARNING"
        return {"status": status, "agents": [sample.to_dict() for sample in samples]}

    def monitor_agents(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:dnsbeat:read")
        samples = self.dnsbeat_service.collect_fleet_health(self.registration_service.list_nodes())
        return {"agents": [sample.to_dict() for sample in samples]}

    def monitor_clusters(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:dnsbeat:read")
        nodes = self.registration_service.list_nodes()
        cluster_ids = sorted({node.cluster_id for node in nodes if node.cluster_id})
        return {
            "clusters": [
                self.dnsbeat_service.collect_cluster_health(str(cluster_id), nodes).to_dict()
                for cluster_id in cluster_ids
            ]
        }

    def monitor_alerts(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:dnsbeat:read")
        alerts: list[dict[str, object]] = []
        for sample in self.dnsbeat_service.collect_fleet_health(self.registration_service.list_nodes()):
            for component in sample.components:
                if component.status != "READY":
                    alerts.append(
                        {
                            "node_id": sample.node_id,
                            "component": component.component,
                            "status": component.status,
                            "message": component.message,
                        }
                    )
        return {"alerts": alerts}

    def set_node_status(
        self, node_id: str, status: str, *, actor: str = "system", role: str = "operator"
    ) -> dict[str, Any]:
        self._require(role, "manager:nodes:operate")
        node = self.registration_service.set_status(node_id, NodeStatus(status))
        self._audit(actor=actor, action="node.status", target=node_id, result=status)
        return {"node": node.to_dict()}

    def _serialize_sync_plan(self, plan: SyncPlan) -> dict[str, Any]:
        return {
            "cluster_id": plan.cluster_id,
            "operation": plan.operation.operation,
            "payload": plan.operation.payload,
            "mode": plan.mode.value,
            "plan_hash": plan.plan_hash,
            "dry_run_required": plan.dry_run_required,
            "targets": [node.to_dict() for node in plan.target_nodes],
        }

    def _serialize_sync_execution(self, execution: SyncExecution) -> dict[str, Any]:
        return {
            "cluster_id": execution.cluster_id,
            "mode": execution.mode.value,
            "plan_hash": execution.plan_hash,
            "accepted": execution.accepted,
            "results": [result.__dict__ for result in execution.results],
        }

    def _build_dnssync_plan(self, payload: dict[str, Any], mode: SyncMode) -> SyncPlan:
        operation = DNSForgeOperation(
            operation=str(payload["operation"]),
            payload=dict(payload.get("payload", {})),
        )
        return self.dnssync_service.build_cluster_plan(
            cluster_id=str(payload["cluster_id"]),
            operation=operation,
            nodes=self.registration_service.list_nodes(),
            mode=mode,
        )

    def dnssync_plans(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:sync:read")
        return {"plans": [self._serialize_sync_plan(plan) for plan in self._dnssync_plans.values()]}

    def create_dnssync_plan(
        self,
        payload: dict[str, Any],
        *,
        actor: str = "system",
        role: str = "operator",
    ) -> dict[str, Any]:
        self._require(role, "manager:sync:operate")
        mode = SyncMode(str(payload.get("mode", SyncMode.DRY_RUN.value)))
        plan = self._build_dnssync_plan(payload, mode)
        self._dnssync_plans[plan.plan_hash] = plan
        self._audit(
            actor=actor,
            action="dnssync.plan",
            target=plan.cluster_id,
            result=plan.plan_hash,
        )
        return {"plan": self._serialize_sync_plan(plan)}

    def validate_dnssync_plan(
        self,
        payload: dict[str, Any],
        *,
        actor: str = "system",
        role: str = "operator",
    ) -> dict[str, Any]:
        self._require(role, "manager:sync:operate")
        plan_hash = payload.get("plan_hash")
        if plan_hash is not None:
            valid = str(plan_hash) in self._dnssync_plans
            return {"valid": valid, "plan_hash": str(plan_hash)}
        plan = self._build_dnssync_plan(payload, SyncMode.DRY_RUN)
        self._audit(actor=actor, action="dnssync.validate", target=plan.cluster_id, result="valid")
        return {"valid": True, "plan": self._serialize_sync_plan(plan)}

    def dry_run_dnssync(
        self,
        payload: dict[str, Any],
        *,
        actor: str = "system",
        role: str = "operator",
    ) -> dict[str, Any]:
        self._require(role, "manager:sync:operate")
        plan = self._build_dnssync_plan(payload, SyncMode.DRY_RUN)
        self._dnssync_plans[plan.plan_hash] = plan
        execution = self.dnssync_service.dry_run(plan)
        self._dnssync_executions.append(execution)
        self._audit(
            actor=actor,
            action="dnssync.dry_run",
            target=plan.cluster_id,
            result="accepted" if execution.accepted else "failed",
            metadata={"plan_hash": execution.plan_hash},
        )
        return {"execution": self._serialize_sync_execution(execution)}

    def apply_dnssync(
        self,
        payload: dict[str, Any],
        *,
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:sync:admin")
        plan = self._build_dnssync_plan(payload, SyncMode.APPLY)
        self._dnssync_plans[plan.plan_hash] = plan
        execution = self.dnssync_service.execute(
            plan,
            self.node_client,
            approved_plan_hash=None
            if payload.get("approved_plan_hash") is None
            else str(payload["approved_plan_hash"]),
        )
        self._dnssync_executions.append(execution)
        self._audit(
            actor=actor,
            action="dnssync.apply",
            target=plan.cluster_id,
            result="accepted" if execution.accepted else "failed",
            metadata={"plan_hash": execution.plan_hash},
        )
        return {"execution": self._serialize_sync_execution(execution)}

    def rollback_dnssync(
        self,
        payload: dict[str, Any],
        *,
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:sync:admin")
        plan = self._build_dnssync_plan(payload, SyncMode.ROLLBACK)
        self._dnssync_plans[plan.plan_hash] = plan
        execution = self.dnssync_service.execute(
            plan,
            self.node_client,
            approved_plan_hash=None
            if payload.get("approved_plan_hash") is None
            else str(payload["approved_plan_hash"]),
        )
        self._dnssync_executions.append(execution)
        self._audit(
            actor=actor,
            action="dnssync.rollback",
            target=plan.cluster_id,
            result="accepted" if execution.accepted else "failed",
            metadata={"plan_hash": execution.plan_hash},
        )
        return {"execution": self._serialize_sync_execution(execution)}

    def dnssync_status(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:sync:read")
        return {
            "plans": [self._serialize_sync_plan(plan) for plan in self._dnssync_plans.values()],
            "executions": [self._serialize_sync_execution(execution) for execution in self._dnssync_executions],
        }

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

    def inventory_agent_compliance(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:inventory:read")
        return self.central_inventory.aggregate_compliance()

    def inventory_agent_compliance_history(
        self,
        fingerprint: str | None = None,
        *,
        role: str = "viewer",
    ) -> dict[str, Any]:
        self._require(role, "manager:inventory:read")
        return {
            "events": [event.to_dict() for event in self.central_inventory.list_agent_compliance_history(fingerprint)]
        }

    def inventory_agent_compliance_trends(
        self,
        fingerprint: str | None = None,
        *,
        role: str = "viewer",
    ) -> dict[str, Any]:
        self._require(role, "manager:inventory:read")
        return self.central_inventory.summarize_agent_compliance_trends(fingerprint)

    def inventory_agent_compliance_report(
        self,
        fingerprint: str | None = None,
        *,
        role: str = "viewer",
    ) -> dict[str, Any]:
        self._require(role, "manager:inventory:read")
        return self.central_inventory.build_agent_compliance_report(fingerprint)

    def update_inventory_agent_compliance(
        self,
        payload: dict[str, Any],
        *,
        actor: str = "system",
        role: str = "operator",
    ) -> dict[str, Any]:
        self._require(role, "manager:inventory:write")
        status = self.central_inventory.update_agent_compliance(payload)
        self._audit(
            actor=actor,
            action="inventory.agent.compliance",
            target=status.fingerprint,
            result=status.compliance.value,
            metadata={"drift_count": status.drift_count},
        )
        return {"agent_compliance": status.to_dict()}

    def trust_enrollments(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:trust:read")
        return {"enrollments": [request.to_dict() for request in self.agent_trust_service.list_enrollments()]}

    def trusted_agents(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:trust:read")
        return {"trusted_agents": [agent.to_dict() for agent in self.agent_trust_service.list_trusted_agents()]}

    def enroll_agent(
        self,
        payload: dict[str, Any],
        *,
        actor: str = "agent",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:trust:write")
        request = self.agent_trust_service.enroll(payload)
        self._audit(actor=actor, action="trust.enroll", target=request.fingerprint, result=request.status.value)
        return {"enrollment": request.to_dict()}

    def approve_agent_enrollment(
        self,
        request_id: str,
        *,
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:trust:admin")
        agent = self.agent_trust_service.approve_enrollment(request_id)
        self._audit(actor=actor, action="trust.approve", target=agent.fingerprint, result=agent.state.value)
        return {"trusted_agent": agent.to_dict(), "agent_token": agent.token}

    def revoke_trusted_agent(
        self,
        fingerprint: str,
        *,
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:trust:admin")
        agent = self.agent_trust_service.revoke_trusted_agent(fingerprint)
        self._audit(actor=actor, action="trust.revoke", target=fingerprint, result=agent.state.value)
        return {"trusted_agent": agent.to_dict()}

    def rotate_trusted_agent_token(
        self,
        fingerprint: str,
        *,
        reason: str = "token-rotation",
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:trust:admin")
        agent = self.agent_trust_service.rotate_trusted_agent_token(fingerprint, reason=reason)
        self._audit(actor=actor, action="trust.token.rotate", target=fingerprint, result="rotated")
        return {"trusted_agent": agent.to_dict(), "agent_token": agent.token}

    def trust_policies(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:trust:read")
        return {"policies": [policy.to_dict() for policy in self.agent_trust_service.list_policies()]}

    def create_trust_policy(
        self,
        payload: dict[str, Any],
        *,
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:trust:admin")
        policy = self.agent_trust_service.create_policy(payload)
        self._audit(actor=actor, action="trust.policy.create", target=policy.policy_id, result="created")
        return {"policy": policy.to_dict()}

    def evaluate_trust_policy(
        self,
        request_id: str,
        policy_id: str,
        *,
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:trust:admin")
        return self.agent_trust_service.evaluate_enrollment(request_id, policy_id)

    def trust_rotations(self, fingerprint: str | None = None, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:trust:read")
        return {"rotations": [record.to_dict() for record in self.agent_trust_service.list_rotations(fingerprint)]}

    def rotate_trusted_agent_certificate(
        self,
        fingerprint: str,
        *,
        public_key: str | None = None,
        reason: str = "certificate-rotation",
        actor: str = "system",
        role: str = "admin",
    ) -> dict[str, Any]:
        self._require(role, "manager:trust:admin")
        agent = self.agent_trust_service.rotate_trusted_agent_certificate(
            fingerprint,
            public_key=public_key,
            reason=reason,
        )
        self._audit(actor=actor, action="trust.certificate.rotate", target=fingerprint, result="rotated")
        return {"trusted_agent": agent.to_dict()}

    def audit_events(self, *, role: str = "viewer") -> dict[str, Any]:
        self._require(role, "manager:audit:read")
        return {"events": [event.to_dict() for event in self.audit_repository.list()]}


def create_app(
    registration_service: NodeRegistrationService | None = None,
    central_inventory_repository: CentralInventoryRepository | None = None,
    agent_trust_service: AgentTrustService | None = None,
) -> ManagerApplication:
    """Return the framework-neutral Manager app core."""
    return ManagerApplication(
        registration_service=registration_service,
        central_inventory_repository=central_inventory_repository,
        agent_trust_service=agent_trust_service,
    )
