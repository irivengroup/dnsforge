from __future__ import annotations

from dnsforge_manager.domain.dnssync.models import DNSForgeOperation
from dnsforge_manager.application.dnssync.dnssync_service import DNSSyncService
from dnsforge_manager.domain.dnssync.models import SyncExecution, SyncMode, SyncPlan
from dnsforge_manager.domain.workflows.models import ManagerChangeRequest
from dnsforge_manager.infrastructure.dnssync.client import DNSForgeNodeClient
from dnsforge_manager.domain.inventory.models import ManagedNode


class ManagerChangeWorkflow:
    def __init__(self, sync_service: DNSSyncService | None = None) -> None:
        self.sync_service = sync_service or DNSSyncService()
        self._approved_plan_hashes: set[str] = set()

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
        execution = self.sync_service.dry_run(self.plan_cluster_change(request, nodes, mode=SyncMode.DRY_RUN))
        self._approved_plan_hashes.add(execution.plan_hash)
        return execution

    def submit_cluster_change(
        self,
        request: ManagerChangeRequest,
        nodes: tuple[ManagedNode, ...],
        client: DNSForgeNodeClient,
        *,
        approved_plan_hash: str | None = None,
    ) -> SyncExecution:
        plan = self.plan_cluster_change(request, nodes, mode=SyncMode.APPLY)
        allowed_hash = approved_plan_hash or (plan.plan_hash if plan.plan_hash in self._approved_plan_hashes else None)
        return self.sync_service.execute(plan, client, approved_plan_hash=allowed_hash)

    def rollback_cluster_change(
        self,
        request: ManagerChangeRequest,
        nodes: tuple[ManagedNode, ...],
        client: DNSForgeNodeClient,
        *,
        approved_plan_hash: str | None = None,
    ) -> SyncExecution:
        plan = self.plan_cluster_change(request, nodes, mode=SyncMode.ROLLBACK)
        allowed_hash = approved_plan_hash or (plan.plan_hash if plan.plan_hash in self._approved_plan_hashes else None)
        return self.sync_service.execute(plan, client, approved_plan_hash=allowed_hash)
