from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from dnsforge_manager.domain.workflows.models import ChangeRequestStatus, ManagerChangeRequest


class ChangeRequestRepository:
    def save(self, change: ManagerChangeRequest) -> ManagerChangeRequest:  # pragma: no cover - protocol-style base
        raise NotImplementedError

    def get(self, change_id: str) -> ManagerChangeRequest:  # pragma: no cover - protocol-style base
        raise NotImplementedError

    def list(self) -> tuple[ManagerChangeRequest, ...]:  # pragma: no cover - protocol-style base
        raise NotImplementedError

    def update_status(
        self,
        change_id: str,
        status: ChangeRequestStatus,
        **fields: object,
    ) -> ManagerChangeRequest:
        change = self.get(change_id)
        updated = replace(change, status=status, updated_at=datetime.now(timezone.utc).isoformat(), **fields)
        return self.save(updated)


class InMemoryChangeRequestRepository(ChangeRequestRepository):
    def __init__(self) -> None:
        self._changes: dict[str, ManagerChangeRequest] = {}

    def save(self, change: ManagerChangeRequest) -> ManagerChangeRequest:
        self._changes[change.change_id] = change
        return change

    def get(self, change_id: str) -> ManagerChangeRequest:
        try:
            return self._changes[change_id]
        except KeyError as exc:
            raise KeyError(f"unknown Manager change request: {change_id}") from exc

    def list(self) -> tuple[ManagerChangeRequest, ...]:
        return tuple(self._changes[key] for key in sorted(self._changes))
