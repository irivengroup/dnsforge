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
        description="manager inventory, audit and change request foundation",
        statements=(
            "CREATE TABLE IF NOT EXISTS manager_nodes (node_id TEXT PRIMARY KEY, payload JSONB NOT NULL);",
            "CREATE TABLE IF NOT EXISTS manager_audit_events (event_id BIGSERIAL PRIMARY KEY, payload JSONB NOT NULL);",
            "CREATE TABLE IF NOT EXISTS manager_change_requests (change_id TEXT PRIMARY KEY, payload JSONB NOT NULL);",
        ),
    ),
)
