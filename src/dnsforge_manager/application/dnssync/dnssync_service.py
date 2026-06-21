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
from dnsforge_manager.infrastructure.concurrency import ParallelExecutor


class DNSSyncService:
    """Manager sub-module that orchestrates DNS operations through DNSForge agents only."""

    def __init__(self, executor: ParallelExecutor | None = None) -> None:
        self.executor = executor or ParallelExecutor()

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
        results = self.executor.map_ordered(
            plan.target_nodes,
            lambda node: DNSForgeOperationResult(node.node_id, True, "dry-run"),
        )
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
        results = self.executor.map_ordered(
            plan.target_nodes,
            lambda node: client.submit(node.node_id, operation),
        )
        return SyncExecution(cluster_id=plan.cluster_id, results=results, mode=plan.mode, plan_hash=plan.plan_hash)

    async def execute_async(
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
        results = await self.executor.amap_ordered(
            plan.target_nodes,
            lambda node: client.submit(node.node_id, operation),
        )
        return SyncExecution(cluster_id=plan.cluster_id, results=results, mode=plan.mode, plan_hash=plan.plan_hash)
