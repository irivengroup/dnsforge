from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PostgreSQLScalePolicy:
    """Enterprise storage defaults for multi-billion-row Manager datasets."""

    batch_size: int = 10000
    server_side_cursor_size: int = 50000
    history_partition_count: int = 64
    statement_timeout_ms: int = 30000


MANAGER_SCALE_SQL: tuple[str, ...] = (
    "CREATE INDEX IF NOT EXISTS idx_agents_payload_profile ON agents ((payload->>'profile'));",
    "CREATE INDEX IF NOT EXISTS idx_agents_payload_cluster ON agents ((payload->>'cluster'));",
    "CREATE INDEX IF NOT EXISTS idx_agents_payload_hostname ON agents ((payload->>'hostname'));",
    "CREATE INDEX IF NOT EXISTS idx_clusters_payload_site_env ON clusters ((payload->>'site'), (payload->>'environment'));",
    "CREATE INDEX IF NOT EXISTS idx_agent_status_payload_site_cluster ON agent_status ((payload->>'site'), (payload->>'cluster'));",
    "CREATE INDEX IF NOT EXISTS idx_agent_compliance_payload_checked ON agent_compliance ((payload->>'last_checked'));",
    "CREATE INDEX IF NOT EXISTS idx_dnssync_executions_payload_cluster_mode ON dnssync_executions ((payload->>'cluster_id'), (payload->>'mode'));",
    "CREATE INDEX IF NOT EXISTS idx_dnssync_executions_payload_plan_hash ON dnssync_executions ((payload->>'plan_hash'));",
    "CREATE INDEX IF NOT EXISTS idx_manager_audit_events_payload_target ON manager_audit_events ((payload->>'target'));",
)


def batched(items: tuple[object, ...], batch_size: int) -> tuple[tuple[object, ...], ...]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    return tuple(items[index : index + batch_size] for index in range(0, len(items), batch_size))
