from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from dnsforge_manager.application.persistence import ChangeRequestLock
from dnsforge_manager.domain.change_management.models import (
    ChangeApproval,
    ChangeExecution,
    ChangeLifecycleStatus,
    ChangeRequest,
    ChangeRollback,
)
from dnsforge_manager.infrastructure.persistence import JsonDocumentStore


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ChangeManagementRepository:
    def save_request(self, change: ChangeRequest) -> ChangeRequest:  # pragma: no cover - port-style base
        raise NotImplementedError

    def get_request(self, change_id: str) -> ChangeRequest:  # pragma: no cover - port-style base
        raise NotImplementedError

    def list_requests(self) -> tuple[ChangeRequest, ...]:  # pragma: no cover - port-style base
        raise NotImplementedError

    def save_approval(self, approval: ChangeApproval) -> ChangeApproval:  # pragma: no cover - port-style base
        raise NotImplementedError

    def list_approvals(self, change_id: str | None = None) -> tuple[ChangeApproval, ...]:  # pragma: no cover
        raise NotImplementedError

    def save_execution(self, execution: ChangeExecution) -> ChangeExecution:  # pragma: no cover - port-style base
        raise NotImplementedError

    def list_executions(self, change_id: str | None = None) -> tuple[ChangeExecution, ...]:  # pragma: no cover
        raise NotImplementedError

    def save_rollback(self, rollback: ChangeRollback) -> ChangeRollback:  # pragma: no cover - port-style base
        raise NotImplementedError

    def list_rollbacks(self, change_id: str | None = None) -> tuple[ChangeRollback, ...]:  # pragma: no cover
        raise NotImplementedError

    def update_status(
        self,
        change_id: str,
        status: ChangeLifecycleStatus,
        **fields: object,
    ) -> ChangeRequest:
        change = self.get_request(change_id)
        updated = replace(
            change,
            status=status,
            reviewed_by=_optional_str(fields.get("reviewed_by", change.reviewed_by)),
            approved_by=_optional_str(fields.get("approved_by", change.approved_by)),
            scheduled_at=_optional_str(fields.get("scheduled_at", change.scheduled_at)),
            failure_reason=_optional_str(fields.get("failure_reason", change.failure_reason)),
            updated_at=_now(),
        )
        return self.save_request(updated)


class InMemoryChangeManagementRepository(ChangeManagementRepository):
    def __init__(self) -> None:
        self._requests: dict[str, ChangeRequest] = {}
        self._approvals: list[ChangeApproval] = []
        self._executions: list[ChangeExecution] = []
        self._rollbacks: list[ChangeRollback] = []

    def save_request(self, change: ChangeRequest) -> ChangeRequest:
        self._requests[change.change_id] = change
        return change

    def get_request(self, change_id: str) -> ChangeRequest:
        try:
            return self._requests[change_id]
        except KeyError as exc:
            raise KeyError(f"unknown Manager change request: {change_id}") from exc

    def list_requests(self) -> tuple[ChangeRequest, ...]:
        return tuple(self._requests[key] for key in sorted(self._requests))

    def save_approval(self, approval: ChangeApproval) -> ChangeApproval:
        self._approvals.append(approval)
        return approval

    def list_approvals(self, change_id: str | None = None) -> tuple[ChangeApproval, ...]:
        return tuple(item for item in self._approvals if change_id is None or item.change_id == change_id)

    def save_execution(self, execution: ChangeExecution) -> ChangeExecution:
        self._executions.append(execution)
        return execution

    def list_executions(self, change_id: str | None = None) -> tuple[ChangeExecution, ...]:
        return tuple(item for item in self._executions if change_id is None or item.change_id == change_id)

    def save_rollback(self, rollback: ChangeRollback) -> ChangeRollback:
        self._rollbacks.append(rollback)
        return rollback

    def list_rollbacks(self, change_id: str | None = None) -> tuple[ChangeRollback, ...]:
        return tuple(item for item in self._rollbacks if change_id is None or item.change_id == change_id)


class JsonChangeManagementRepository(ChangeManagementRepository):
    def __init__(self, path: Path) -> None:
        self.store = JsonDocumentStore(path)
        self.lock = ChangeRequestLock(path.with_suffix(path.suffix + ".lock"))

    def _read_requests(self) -> dict[str, ChangeRequest]:
        return self.store.read_items("change_requests", ChangeRequest.from_dict)

    def _write_requests(self, changes: dict[str, ChangeRequest]) -> None:
        self.store.write_items(
            "change_requests",
            (change.to_dict() for change in sorted(changes.values(), key=lambda item: item.change_id)),
        )

    def save_request(self, change: ChangeRequest) -> ChangeRequest:
        with self.lock.acquire():
            changes = self._read_requests()
            changes[change.change_id] = change
            self._write_requests(changes)
        return change

    def get_request(self, change_id: str) -> ChangeRequest:
        try:
            return self._read_requests()[change_id]
        except KeyError as exc:
            raise KeyError(f"unknown Manager change request: {change_id}") from exc

    def list_requests(self) -> tuple[ChangeRequest, ...]:
        changes = self._read_requests()
        return tuple(changes[key] for key in sorted(changes))

    def save_approval(self, approval: ChangeApproval) -> ChangeApproval:
        approvals = list(self.list_approvals())
        approvals.append(approval)
        self.store.write_items("change_approvals", (item.to_dict() for item in approvals))
        return approval

    def list_approvals(self, change_id: str | None = None) -> tuple[ChangeApproval, ...]:
        values = tuple(self.store.read_items("change_approvals", ChangeApproval.from_dict).values())
        return tuple(item for item in values if change_id is None or item.change_id == change_id)

    def save_execution(self, execution: ChangeExecution) -> ChangeExecution:
        executions = list(self.list_executions())
        executions.append(execution)
        self.store.write_items("change_executions", (item.to_dict() for item in executions))
        return execution

    def list_executions(self, change_id: str | None = None) -> tuple[ChangeExecution, ...]:
        values = tuple(self.store.read_items("change_executions", ChangeExecution.from_dict).values())
        return tuple(item for item in values if change_id is None or item.change_id == change_id)

    def save_rollback(self, rollback: ChangeRollback) -> ChangeRollback:
        rollbacks = list(self.list_rollbacks())
        rollbacks.append(rollback)
        self.store.write_items("change_rollbacks", (item.to_dict() for item in rollbacks))
        return rollback

    def list_rollbacks(self, change_id: str | None = None) -> tuple[ChangeRollback, ...]:
        values = tuple(self.store.read_items("change_rollbacks", ChangeRollback.from_dict).values())
        return tuple(item for item in values if change_id is None or item.change_id == change_id)


def _optional_str(value: object) -> str | None:
    return None if value is None else str(value)
