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
    ManagerSchemaMigration(
        version="004",
        description="central inventory source of truth",
        statements=(
            "CREATE TABLE IF NOT EXISTS sites (site_id TEXT PRIMARY KEY, payload JSONB NOT NULL);",
            "CREATE TABLE IF NOT EXISTS clusters (cluster_id TEXT PRIMARY KEY, payload JSONB NOT NULL);",
            "CREATE TABLE IF NOT EXISTS agents (fingerprint TEXT PRIMARY KEY, payload JSONB NOT NULL);",
            "CREATE TABLE IF NOT EXISTS environments (environment_id TEXT PRIMARY KEY, payload JSONB NOT NULL);",
            "CREATE TABLE IF NOT EXISTS agent_status (fingerprint TEXT PRIMARY KEY, payload JSONB NOT NULL);",
            "CREATE INDEX IF NOT EXISTS idx_agents_site ON agents ((payload->>'site'));",
            "CREATE INDEX IF NOT EXISTS idx_agent_status_readiness ON agent_status ((payload->>'readiness'));",
        ),
    ),
    ManagerSchemaMigration(
        version="005",
        description="manager agent compliance aggregation",
        statements=(
            "CREATE TABLE IF NOT EXISTS agent_compliance (fingerprint TEXT PRIMARY KEY, payload JSONB NOT NULL);",
            "CREATE INDEX IF NOT EXISTS idx_agent_compliance_state ON agent_compliance ((payload->>'compliance'));",
            "CREATE INDEX IF NOT EXISTS idx_agent_compliance_drift_count ON agent_compliance (((payload->>'drift_count')::INTEGER));",
        ),
    ),
    ManagerSchemaMigration(
        version="006",
        description="manager agent compliance history",
        statements=(
            "CREATE TABLE IF NOT EXISTS agent_compliance_history (event_id TEXT PRIMARY KEY, payload JSONB NOT NULL);",
            "CREATE INDEX IF NOT EXISTS idx_agent_compliance_history_fingerprint ON agent_compliance_history ((payload->>'fingerprint'));",
            "CREATE INDEX IF NOT EXISTS idx_agent_compliance_history_state ON agent_compliance_history ((payload->>'compliance'));",
            "CREATE INDEX IF NOT EXISTS idx_agent_compliance_history_observed_at ON agent_compliance_history ((payload->>'observed_at'));",
        ),
    ),
)
