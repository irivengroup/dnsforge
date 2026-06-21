from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Any

from dnsforge_manager.application.change_management.repository import (
    ChangeManagementRepository,
    InMemoryChangeManagementRepository,
)
from dnsforge_manager.domain.change_management.models import (
    ChangeApproval,
    ChangeExecution,
    ChangeGate,
    ChangeGateStatus,
    ChangeLifecycleStatus,
    ChangePlan,
    ChangeRequest,
    ChangeRiskLevel,
    ChangeRollback,
    ChangeTargetScope,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ChangeManagementService:
    """Enterprise change orchestration service.

    The service owns Manager-side approval state. It does not edit BIND directly;
    execution remains an orchestration decision gated by inventory/trust/compliance/readiness signals.
    """

    def __init__(self, repository: ChangeManagementRepository | None = None) -> None:
        self.repository = repository or InMemoryChangeManagementRepository()

    def create_change(self, payload: dict[str, Any], *, requested_by: str = "system") -> ChangeRequest:
        request = ChangeRequest(
            title=str(payload.get("title", payload.get("operation", "change"))),
            description=str(payload.get("description", "")),
            requested_by=str(payload.get("requested_by", requested_by)),
            target_scope=ChangeTargetScope(str(payload.get("target_scope", ChangeTargetScope.CLUSTER.value))),
            target_id=str(payload.get("target_id", payload.get("cluster_id", "default"))),
            operation=str(payload["operation"]),
            payload=dict(payload.get("payload", {})),
            risk_level=self.analyze_risk(str(payload["operation"]), str(payload.get("target_scope", "CLUSTER"))),
        )
        change = replace(request, change_id=request.change_id or f"chg-{request.stable_hash[:12]}", updated_at=_now())
        return self.repository.save_request(change)

    def list_changes(self) -> tuple[ChangeRequest, ...]:
        return self.repository.list_requests()

    def get_change(self, change_id: str) -> ChangeRequest:
        return self.repository.get_request(change_id)

    def review_change(self, change_id: str, *, reviewer: str = "system") -> ChangeRequest:
        change = self.repository.get_request(change_id)
        if change.status != ChangeLifecycleStatus.DRAFT:
            raise PermissionError("only draft changes can be reviewed")
        return self.repository.update_status(change_id, ChangeLifecycleStatus.REVIEWED, reviewed_by=reviewer)

    def approve_change(self, change_id: str, *, approver: str = "system", comment: str = "") -> ChangeRequest:
        change = self.repository.get_request(change_id)
        if change.status not in {ChangeLifecycleStatus.DRAFT, ChangeLifecycleStatus.REVIEWED}:
            raise PermissionError("only draft or reviewed changes can be approved")
        self.repository.save_approval(ChangeApproval(change_id=change_id, approver=approver, comment=comment))
        return self.repository.update_status(change_id, ChangeLifecycleStatus.APPROVED, approved_by=approver)

    def build_plan(self, change_id: str, signals: dict[str, Any] | None = None) -> ChangePlan:
        change = self.repository.get_request(change_id)
        runtime_signals = signals or {}
        gates = self._build_gates(runtime_signals)
        return ChangePlan(
            change_id=change.change_id,
            target_scope=change.target_scope,
            target_id=change.target_id,
            risk_level=change.risk_level,
            steps=self._steps_for(change),
            gates=tuple(gates),
        )

    def execute_change(
        self,
        change_id: str,
        *,
        actor: str = "system",
        signals: dict[str, Any] | None = None,
    ) -> ChangeExecution:
        change = self.repository.get_request(change_id)
        if change.status != ChangeLifecycleStatus.APPROVED:
            raise PermissionError("only approved changes can be executed")
        plan = self.build_plan(change_id, signals=signals)
        if not plan.accepted:
            blocked = ", ".join(gate.name for gate in plan.gates if gate.status == ChangeGateStatus.BLOCKED)
            self.repository.update_status(change_id, ChangeLifecycleStatus.FAILED, failure_reason=blocked)
            raise PermissionError("change execution blocked by gates: " + blocked)
        self.repository.update_status(change_id, ChangeLifecycleStatus.EXECUTING)
        execution = ChangeExecution(
            change_id=change_id,
            result=ChangeLifecycleStatus.COMPLETED,
            plan_hash=plan.plan_hash,
            targets=(change.target_id,),
            completed_at=_now(),
            message=f"executed by {actor}",
        )
        self.repository.save_execution(execution)
        self.repository.update_status(change_id, ChangeLifecycleStatus.COMPLETED)
        return execution

    def rollback_change(
        self,
        change_id: str,
        *,
        reason: str = "operator-request",
        actor: str = "system",
    ) -> ChangeRollback:
        change = self.repository.get_request(change_id)
        if change.status not in {ChangeLifecycleStatus.COMPLETED, ChangeLifecycleStatus.FAILED}:
            raise PermissionError("only completed or failed changes can be rolled back")
        rollback = ChangeRollback(change_id=change_id, reason=reason, triggered_by=actor)
        self.repository.save_rollback(rollback)
        self.repository.update_status(change_id, ChangeLifecycleStatus.ROLLED_BACK)
        return rollback

    def status(self, change_id: str) -> dict[str, object]:
        change = self.repository.get_request(change_id)
        return {
            "change": change.to_dict(),
            "approvals": [approval.to_dict() for approval in self.repository.list_approvals(change_id)],
            "executions": [execution.to_dict() for execution in self.repository.list_executions(change_id)],
            "rollbacks": [rollback.to_dict() for rollback in self.repository.list_rollbacks(change_id)],
        }

    def analyze_risk(self, operation: str, target_scope: str) -> ChangeRiskLevel:
        normalized = operation.lower()
        scope = target_scope.upper()
        if "migration" in normalized or scope == ChangeTargetScope.CATALOG.value:
            return ChangeRiskLevel.CRITICAL
        if "delete" in normalized or "rollback" in normalized:
            return ChangeRiskLevel.HIGH
        if "dnssec" in normalized or "catalog" in normalized or scope == ChangeTargetScope.CLUSTER.value:
            return ChangeRiskLevel.MEDIUM
        return ChangeRiskLevel.LOW

    def _build_gates(self, signals: dict[str, Any]) -> list[ChangeGate]:
        readiness = str(signals.get("readiness", "READY"))
        trust = str(signals.get("trust", "TRUSTED"))
        compliance = str(signals.get("compliance", "COMPLIANT"))
        return [
            _gate("readiness", readiness == "READY", f"agent readiness is {readiness}"),
            _gate("trust", trust in {"TRUSTED", "APPROVED"}, f"agent trust state is {trust}"),
            _gate(
                "compliance",
                compliance in {"COMPLIANT", "WARNING"},
                f"agent compliance state is {compliance}",
            ),
        ]

    def _steps_for(self, change: ChangeRequest) -> tuple[str, ...]:
        return (
            "resolve-targets-from-inventory",
            "validate-agent-trust",
            "validate-agent-readiness",
            "validate-agent-compliance",
            f"orchestrate-{change.operation}-through-dnsforge-agent",
            "verify-post-change-compliance",
        )


def _gate(name: str, passed: bool, message: str) -> ChangeGate:
    status = ChangeGateStatus.PASSED if passed else ChangeGateStatus.BLOCKED
    return ChangeGate(name=name, status=status, message=message)
