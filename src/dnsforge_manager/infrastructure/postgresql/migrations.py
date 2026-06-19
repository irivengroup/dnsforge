from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ManagerSchemaMigration:
    version: str
    description: str
    statements: tuple[str, ...]


MANAGER_SCHEMA_MIGRATIONS: tuple[ManagerSchemaMigration, ...] = (
    ManagerSchemaMigration(
        version="001",
        description="manager nodes inventory",
        statements=(
            "CREATE TABLE IF NOT EXISTS manager_nodes (node_id TEXT PRIMARY KEY, payload JSONB NOT NULL);",
            "CREATE INDEX IF NOT EXISTS idx_manager_nodes_payload_status ON manager_nodes ((payload->>'status'));",
        ),
    ),
    ManagerSchemaMigration(
        version="002",
        description="manager change requests",
        statements=(
            "CREATE TABLE IF NOT EXISTS manager_change_requests (change_id TEXT PRIMARY KEY, payload JSONB NOT NULL);",
            "CREATE INDEX IF NOT EXISTS idx_manager_change_requests_status ON manager_change_requests ((payload->>'status'));",
        ),
    ),
    ManagerSchemaMigration(
        version="003",
        description="manager audit events",
        statements=(
            "CREATE TABLE IF NOT EXISTS manager_audit_events (event_id BIGSERIAL PRIMARY KEY, payload JSONB NOT NULL);",
            "CREATE INDEX IF NOT EXISTS idx_manager_audit_events_action ON manager_audit_events ((payload->>'action'));",
        ),
    ),
)
