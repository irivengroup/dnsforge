from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RequiredEvent:
    name: str
    category: str


@dataclass(frozen=True)
class EventContract:
    required_events: tuple[RequiredEvent, ...]


PUBLIC_EVENT_CONTRACT = EventContract(
    required_events=(
        RequiredEvent("ZoneCreated", "zone"),
        RequiredEvent("ZoneUpdated", "zone"),
        RequiredEvent("ZoneDeleted", "zone"),
        RequiredEvent("ZoneRollback", "zone"),
        RequiredEvent("MigrationStarted", "migration"),
        RequiredEvent("MigrationCompleted", "migration"),
        RequiredEvent("MigrationFailed", "migration"),
        RequiredEvent("CatalogSyncCompleted", "catalog"),
        RequiredEvent("CatalogRepairCompleted", "catalog"),
        RequiredEvent("ClusterAuditCompleted", "cluster"),
        RequiredEvent("DNSSECRotationCompleted", "dnssec"),
        RequiredEvent("DisasterSnapshotCreated", "disaster"),
        RequiredEvent("DisasterRestoreCompleted", "disaster"),
    )
)
