from __future__ import annotations

from dnsforge_manager.domain.dnssync.models import SyncExecution, SyncPlan


class DNSSyncRepository:
    """Repository for DNSSync orchestration plans and execution history.

    The default implementation is intentionally in-memory so JSON remains the
    default Manager backend. PostgreSQL backends can implement the same small
    contract with partitioned execution-history tables for large fleets.
    """

    def __init__(self) -> None:
        self._plans: dict[str, SyncPlan] = {}
        self._executions: list[SyncExecution] = []

    def save_plan(self, plan: SyncPlan) -> None:
        self._plans[plan.plan_hash] = plan

    def get_plan(self, plan_hash: str) -> SyncPlan | None:
        return self._plans.get(plan_hash)

    def list_plans(self) -> tuple[SyncPlan, ...]:
        return tuple(self._plans.values())

    def save_execution(self, execution: SyncExecution) -> None:
        self._executions.append(execution)

    def list_executions(self, *, cluster_id: str | None = None) -> tuple[SyncExecution, ...]:
        if cluster_id is None:
            return tuple(self._executions)
        return tuple(execution for execution in self._executions if execution.cluster_id == cluster_id)
