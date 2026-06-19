from __future__ import annotations

import json

from dnsforge_manager.domain.audit.models import ManagerAuditEvent
from dnsforge_manager.infrastructure.persistence.postgresql.connection import ConnectionLike


class PostgreSQLManagerAuditRepository:
    """Append-only PostgreSQL audit repository for Manager events."""

    def __init__(self, connection: ConnectionLike) -> None:
        self.connection = connection

    def append(self, event: ManagerAuditEvent) -> ManagerAuditEvent:
        payload = json.dumps(event.to_dict(), sort_keys=True)
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO manager_audit_events (payload) VALUES (%s::jsonb)", (payload,))
        self.connection.commit()
        return event

    def list(self) -> tuple[ManagerAuditEvent, ...]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT payload FROM manager_audit_events ORDER BY event_id")
        return tuple(ManagerAuditEvent(**_payload(row)) for row in cursor.fetchall())


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
