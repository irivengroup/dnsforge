from __future__ import annotations

from dataclasses import dataclass

from dnsforge_manager.dnssync.client import DNSForgeNodeClient, DNSForgeOperation, DNSForgeOperationResult
from dnsforge_manager.inventory.models import ManagedNode


@dataclass(frozen=True)
class SyncPlan:
    cluster_id: str
    operation: DNSForgeOperation
    target_nodes: tuple[ManagedNode, ...]


@dataclass(frozen=True)
class SyncExecution:
    cluster_id: str
    results: tuple[DNSForgeOperationResult, ...]

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
    ) -> SyncPlan:
        targets = tuple(node for node in nodes if node.cluster_id == cluster_id)
        if not targets:
            raise ValueError(f"no DNSForge nodes registered for cluster: {cluster_id}")
        return SyncPlan(cluster_id=cluster_id, operation=operation, target_nodes=targets)

    def execute(self, plan: SyncPlan, client: DNSForgeNodeClient) -> SyncExecution:
        results = tuple(client.submit(node.node_id, plan.operation) for node in plan.target_nodes)
        return SyncExecution(cluster_id=plan.cluster_id, results=results)
