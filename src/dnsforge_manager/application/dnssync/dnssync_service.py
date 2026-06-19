from __future__ import annotations

from dnsforge_manager.application.security.agent_trust_service import AgentTrustService
from dnsforge_manager.domain.dnssync.models import (
    DNSForgeOperation,
    DNSForgeOperationResult,
    SyncExecution,
    SyncMode,
    SyncPlan,
)
from dnsforge_manager.domain.inventory.models import ManagedNode, NodeStatus
from dnsforge_manager.infrastructure.dnssync.client import DNSForgeNodeClient


class DNSSyncService:
    """Manager sub-module that orchestrates changes through DNSForge agents only."""

    def build_cluster_plan(
        self,
        *,
        cluster_id: str,
        operation: DNSForgeOperation,
        nodes: tuple[ManagedNode, ...],
        mode: SyncMode = SyncMode.APPLY,
    ) -> SyncPlan:
        targets = tuple(
            node
            for node in nodes
            if node.cluster_id == cluster_id
            and node.status not in {NodeStatus.DISABLED, NodeStatus.UNREACHABLE}
            and node.trust_state == "approved"
        )
        if not targets:
            raise ValueError(f"no active approved DNSForge nodes registered for cluster: {cluster_id}")
        return SyncPlan(cluster_id=cluster_id, operation=operation, target_nodes=targets, mode=mode)

    def dry_run(self, plan: SyncPlan) -> SyncExecution:
        results = tuple(DNSForgeOperationResult(node.node_id, True, "dry-run") for node in plan.target_nodes)
        return SyncExecution(
            cluster_id=plan.cluster_id, results=results, mode=SyncMode.DRY_RUN, plan_hash=plan.plan_hash
        )

    def execute(
        self,
        plan: SyncPlan,
        client: DNSForgeNodeClient,
        *,
        approved_plan_hash: str | None = None,
    ) -> SyncExecution:
        if plan.mode == SyncMode.DRY_RUN:
            return self.dry_run(plan)
        if plan.dry_run_required and approved_plan_hash != plan.plan_hash:
            raise PermissionError("DNSSync apply/rollback requires an approved dry-run plan hash")
        for node in plan.target_nodes:
            AgentTrustService.assert_trusted(node)
        operation = plan.operation
        if plan.mode == SyncMode.ROLLBACK:
            operation = DNSForgeOperation(
                operation=f"rollback.{plan.operation.operation}",
                payload={**plan.operation.payload, "rollback_plan_hash": plan.plan_hash},
            )
        results = tuple(client.submit(node.node_id, operation) for node in plan.target_nodes)
        return SyncExecution(cluster_id=plan.cluster_id, results=results, mode=plan.mode, plan_hash=plan.plan_hash)
