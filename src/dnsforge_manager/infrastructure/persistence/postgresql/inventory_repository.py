from __future__ import annotations

import json
from dataclasses import replace

from dnsforge_manager.domain.inventory.models import ManagedNode, NodeStatus
from dnsforge_manager.infrastructure.persistence.postgresql.connection import ConnectionLike


class PostgreSQLNodeInventoryRepository:
    """PostgreSQL-backed Manager node inventory repository.

    The adapter is intentionally DB-API compatible and does not import a concrete
    PostgreSQL driver. Deployment code may inject a psycopg/psycopg2 connection.
    """

    def __init__(self, connection: ConnectionLike) -> None:
        self.connection = connection

    def register(self, node: ManagedNode) -> ManagedNode:
        if self._exists(node.node_id):
            raise ValueError(f"node already registered: {node.node_id}")
        return self.upsert(node)

    def upsert(self, node: ManagedNode) -> ManagedNode:
        payload = json.dumps(node.to_dict(include_token=True), sort_keys=True)
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO manager_nodes (node_id, payload)
            VALUES (%s, %s::jsonb)
            ON CONFLICT (node_id) DO UPDATE SET payload = EXCLUDED.payload
            """,
            (node.node_id, payload),
        )
        self.connection.commit()
        return node

    def get(self, node_id: str) -> ManagedNode:
        cursor = self.connection.cursor()
        cursor.execute("SELECT payload FROM manager_nodes WHERE node_id = %s", (node_id,))
        row = cursor.fetchone()
        if row is None:
            raise KeyError(f"unknown node: {node_id}")
        return ManagedNode.from_dict(_payload(row))

    def list(self) -> tuple[ManagedNode, ...]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT payload FROM manager_nodes ORDER BY node_id")
        return tuple(ManagedNode.from_dict(_payload(row)) for row in cursor.fetchall())

    def set_status(self, node_id: str, status: NodeStatus) -> ManagedNode:
        return self.upsert(replace(self.get(node_id), status=status))

    def _exists(self, node_id: str) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1 FROM manager_nodes WHERE node_id = %s", (node_id,))
        return cursor.fetchone() is not None


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

''' verifs '''