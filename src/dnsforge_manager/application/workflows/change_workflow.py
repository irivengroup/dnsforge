from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from dnsforge_manager.application.dnsbeat.dnsbeat_service import DNSBeatService
from dnsforge_manager.application.dnssync.dnssync_service import DNSSyncService
from dnsforge_manager.application.workflows.change_repository import (
    ChangeRequestRepository,
    InMemoryChangeRequestRepository,
)
from dnsforge_manager.domain.dnssync.models import DNSForgeOperation, SyncExecution, SyncMode, SyncPlan
from dnsforge_manager.domain.inventory.models import ManagedNode
from dnsforge_manager.domain.workflows.models import ChangeRequestStatus, ManagerChangeRequest
from dnsforge_manager.infrastructure.dnssync.client import DNSForgeNodeClient


class ManagerChangeWorkflow:
    def __init__(
        self,
        sync_service: DNSSyncService | None = None,
        repository: ChangeRequestRepository | None = None,
        dnsbeat_service: DNSBeatService | None = None,
    ) -> None:
        self.sync_service = sync_service or DNSSyncService()
        self.repository = repository or InMemoryChangeRequestRepository()
        self.dnsbeat_service = dnsbeat_service or DNSBeatService()
        self._approved_plan_hashes: set[str] = set()

    def _change_id(self, request: ManagerChangeRequest) -> str:
        return request.change_id or f"chg-{request.stable_hash[:12]}"

    def create_change(self, request: ManagerChangeRequest) -> ManagerChangeRequest:
        now = datetime.now(timezone.utc).isoformat()
        change = replace(
            request,
            change_id=self._change_id(request),
            status=ChangeRequestStatus.PENDING,
            created_at=request.created_at or now,
            updated_at=now,
        )
        return self.repository.save(change)

    def list_changes(self) -> tuple[ManagerChangeRequest, ...]:
        return self.repository.list()

    def get_change(self, change_id: str) -> ManagerChangeRequest:
        return self.repository.get(change_id)

    def approve_change(self, change_id: str, *, actor: str) -> ManagerChangeRequest:
        return self.repository.update_status(change_id, ChangeRequestStatus.APPROVED, approved_by=actor)

    def reject_change(self, change_id: str, *, reason: str | None = None) -> ManagerChangeRequest:
        return self.repository.update_status(change_id, ChangeRequestStatus.REJECTED, failure_reason=reason)

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
        if request.change_id:
            self.repository.update_status(request.change_id, request.status, plan_hash=execution.plan_hash)
        return execution

    def dry_run_change(self, change_id: str, nodes: tuple[ManagedNode, ...]) -> SyncExecution:
        change = self.repository.get(change_id)
        execution = self.dry_run_cluster_change(change, nodes)
        self.repository.update_status(change_id, change.status, plan_hash=execution.plan_hash)
        return execution

    def _assert_targets_healthy(self, plan: SyncPlan) -> None:
        unhealthy = [
            f"{sample.node_id}:{sample.score}"
            for sample in (self.dnsbeat_service.collect_node_health(node) for node in plan.target_nodes)
            if sample.score < 100
        ]
        if unhealthy:
            raise PermissionError("DNSBeat blocked apply because node health is not clean: " + ", ".join(unhealthy))

    def submit_cluster_change(
        self,
        request: ManagerChangeRequest,
        nodes: tuple[ManagedNode, ...],
        client: DNSForgeNodeClient,
        *,
        approved_plan_hash: str | None = None,
    ) -> SyncExecution:
        plan = self.plan_cluster_change(request, nodes, mode=SyncMode.APPLY)
        self._assert_targets_healthy(plan)
        allowed_hash = approved_plan_hash or (plan.plan_hash if plan.plan_hash in self._approved_plan_hashes else None)
        return self.sync_service.execute(plan, client, approved_plan_hash=allowed_hash)

    def apply_change(
        self,
        change_id: str,
        nodes: tuple[ManagedNode, ...],
        client: DNSForgeNodeClient,
        *,
        approved_plan_hash: str | None = None,
    ) -> SyncExecution:
        change = self.repository.get(change_id)
        if change.status != ChangeRequestStatus.APPROVED:
            raise PermissionError("only approved change requests can be applied")
        try:
            execution = self.submit_cluster_change(change, nodes, client, approved_plan_hash=approved_plan_hash)
            self.repository.update_status(
                change_id,
                ChangeRequestStatus.APPLIED,
                plan_hash=execution.plan_hash,
                rollback_plan_hash=execution.plan_hash,
            )
            return execution
        except Exception as exc:
            self.repository.update_status(change_id, ChangeRequestStatus.FAILED, failure_reason=str(exc))
            raise

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

    def rollback_change(
        self,
        change_id: str,
        nodes: tuple[ManagedNode, ...],
        client: DNSForgeNodeClient,
        *,
        approved_plan_hash: str | None = None,
    ) -> SyncExecution:
        change = self.repository.get(change_id)
        if change.status not in {ChangeRequestStatus.APPLIED, ChangeRequestStatus.FAILED}:
            raise PermissionError("only applied or failed change requests can be rolled back")
        execution = self.rollback_cluster_change(change, nodes, client, approved_plan_hash=approved_plan_hash)
        self.repository.update_status(
            change_id, ChangeRequestStatus.ROLLED_BACK, rollback_plan_hash=execution.plan_hash
        )
        return execution
