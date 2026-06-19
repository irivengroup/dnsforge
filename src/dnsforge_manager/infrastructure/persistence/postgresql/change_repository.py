from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timezone

from dnsforge_manager.domain.workflows.models import ChangeRequestStatus, ManagerChangeRequest
from dnsforge_manager.infrastructure.persistence.postgresql.connection import ConnectionLike

_ALLOWED_STATUS_FIELDS = {"approved_by", "plan_hash", "rollback_plan_hash", "failure_reason"}


class PostgreSQLChangeRequestRepository:
    """PostgreSQL-backed Manager change request repository."""

    def __init__(self, connection: ConnectionLike) -> None:
        self.connection = connection

    def save(self, change: ManagerChangeRequest) -> ManagerChangeRequest:
        payload = json.dumps(change.to_dict(), sort_keys=True)
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO manager_change_requests (change_id, payload)
            VALUES (%s, %s::jsonb)
            ON CONFLICT (change_id) DO UPDATE SET payload = EXCLUDED.payload
            """,
            (change.change_id, payload),
        )
        self.connection.commit()
        return change

    def get(self, change_id: str) -> ManagerChangeRequest:
        cursor = self.connection.cursor()
        cursor.execute("SELECT payload FROM manager_change_requests WHERE change_id = %s", (change_id,))
        row = cursor.fetchone()
        if row is None:
            raise KeyError(f"unknown Manager change request: {change_id}")
        return ManagerChangeRequest.from_dict(_payload(row))

    def list(self) -> tuple[ManagerChangeRequest, ...]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT payload FROM manager_change_requests ORDER BY change_id")
        return tuple(ManagerChangeRequest.from_dict(_payload(row)) for row in cursor.fetchall())

    def update_status(
        self,
        change_id: str,
        status: ChangeRequestStatus,
        **fields: object,
    ) -> ManagerChangeRequest:
        unknown_fields = sorted(set(fields) - _ALLOWED_STATUS_FIELDS)
        if unknown_fields:
            raise ValueError("unsupported change status fields: " + ", ".join(unknown_fields))
        change = self.get(change_id)
        updated = replace(
            change,
            status=status,
            approved_by=_optional_str(fields.get("approved_by", change.approved_by)),
            plan_hash=_optional_str(fields.get("plan_hash", change.plan_hash)),
            rollback_plan_hash=_optional_str(fields.get("rollback_plan_hash", change.rollback_plan_hash)),
            failure_reason=_optional_str(fields.get("failure_reason", change.failure_reason)),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        return self.save(updated)


def _optional_str(value: object) -> str | None:
    return None if value is None else str(value)


def _payload(row: object) -> dict[str, object]:
    value = row[0] if isinstance(row, tuple) else row
    if isinstance(value, str):
        parsed = json.loads(value)
        if not isinstance(parsed, dict):
            raise ValueError("PostgreSQL payload must be a JSON object")
        return parsed
    if isinstance(value, dict):
        return value
    raise TypeError("unsupported PostgreSQL payload row")
