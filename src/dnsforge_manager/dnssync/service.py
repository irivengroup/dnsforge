from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from dnsforge_manager.dnssync.client import DNSForgeNodeClient, DNSForgeOperation, DNSForgeOperationResult
from dnsforge_manager.inventory.models import ManagedNode, NodeStatus


class SyncMode(str, Enum):
    DRY_RUN = "dry-run"
    APPLY = "apply"
    ROLLBACK = "rollback"


@dataclass(frozen=True)
class SyncPlan:
    cluster_id: str
    operation: DNSForgeOperation
    target_nodes: tuple[ManagedNode, ...]
    mode: SyncMode = SyncMode.DRY_RUN


@dataclass(frozen=True)
class SyncExecution:
    cluster_id: str
    results: tuple[DNSForgeOperationResult, ...]
    mode: SyncMode = SyncMode.DRY_RUN

    @property
    def accepted(self) -> bool:
        return all(result.accepted for result in self.results)


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
            if node.cluster_id == cluster_id and node.status not in {NodeStatus.DISABLED, NodeStatus.UNREACHABLE}
        )
        if not targets:
            raise ValueError(f"no active DNSForge nodes registered for cluster: {cluster_id}")
        return SyncPlan(cluster_id=cluster_id, operation=operation, target_nodes=targets, mode=mode)

    def dry_run(self, plan: SyncPlan) -> SyncExecution:
        results = tuple(DNSForgeOperationResult(node.node_id, True, "dry-run") for node in plan.target_nodes)
        return SyncExecution(cluster_id=plan.cluster_id, results=results, mode=SyncMode.DRY_RUN)

    def execute(self, plan: SyncPlan, client: DNSForgeNodeClient) -> SyncExecution:
        if plan.mode == SyncMode.DRY_RUN:
            return self.dry_run(plan)
        operation = plan.operation
        if plan.mode == SyncMode.ROLLBACK:
            operation = DNSForgeOperation(
                operation=f"rollback.{plan.operation.operation}",
                payload=plan.operation.payload,
            )
        results = tuple(client.submit(node.node_id, operation) for node in plan.target_nodes)
        return SyncExecution(cluster_id=plan.cluster_id, results=results, mode=plan.mode)
