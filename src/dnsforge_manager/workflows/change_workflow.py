from __future__ import annotations

from dataclasses import dataclass

from dnsforge_manager.dnssync.client import DNSForgeNodeClient, DNSForgeOperation
from dnsforge_manager.dnssync.service import DNSSyncService, SyncExecution, SyncMode, SyncPlan
from dnsforge_manager.inventory.models import ManagedNode


@dataclass(frozen=True)
class ManagerChangeRequest:
    cluster_id: str
    operation: str
    payload: dict[str, object]


class ManagerChangeWorkflow:
    def __init__(self, sync_service: DNSSyncService | None = None) -> None:
        self.sync_service = sync_service or DNSSyncService()

    def plan_cluster_change(
        self,
        request: ManagerChangeRequest,
        nodes: tuple[ManagedNode, ...],
        *,
        mode: SyncMode = SyncMode.DRY_RUN,
    ) -> SyncPlan:
        return self.sync_service.build_cluster_plan(
            cluster_id=request.cluster_id,
            operation=DNSForgeOperation(operation=request.operation, payload=request.payload),
            nodes=nodes,
            mode=mode,
        )

    def dry_run_cluster_change(self, request: ManagerChangeRequest, nodes: tuple[ManagedNode, ...]) -> SyncExecution:
        return self.sync_service.dry_run(self.plan_cluster_change(request, nodes, mode=SyncMode.DRY_RUN))

    def submit_cluster_change(
        self,
        request: ManagerChangeRequest,
        nodes: tuple[ManagedNode, ...],
        client: DNSForgeNodeClient,
    ) -> SyncExecution:
        plan = self.plan_cluster_change(request, nodes, mode=SyncMode.APPLY)
        return self.sync_service.execute(plan, client)

    def rollback_cluster_change(
        self,
        request: ManagerChangeRequest,
        nodes: tuple[ManagedNode, ...],
        client: DNSForgeNodeClient,
    ) -> SyncExecution:
        plan = self.plan_cluster_change(request, nodes, mode=SyncMode.ROLLBACK)
        return self.sync_service.execute(plan, client)
