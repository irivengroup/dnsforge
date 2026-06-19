from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum

from dnsforge_manager.domain.inventory.models import ManagedNode


@dataclass(frozen=True)
class DNSForgeOperation:
    operation: str
    payload: dict[str, object]


@dataclass(frozen=True)
class DNSForgeOperationResult:
    node_id: str
    accepted: bool
    message: str


class SyncMode(str, Enum):
    DRY_RUN = "dry-run"
    APPLY = "apply"
    ROLLBACK = "rollback"


@dataclass(frozen=True)
class SyncPlan:
    cluster_id: str
    operation: DNSForgeOperation
    target_nodes: tuple[ManagedNode, ...]
    mode: SyncMode = SyncMode.DRY_RUN
    dry_run_required: bool = True

    @property
    def plan_hash(self) -> str:
        payload = {
            "cluster_id": self.cluster_id,
            "operation": self.operation.operation,
            "payload": self.operation.payload,
            "targets": [node.node_id for node in self.target_nodes],
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SyncExecution:
    cluster_id: str
    results: tuple[DNSForgeOperationResult, ...]
    mode: SyncMode = SyncMode.DRY_RUN
    plan_hash: str = ""

    @property
    def accepted(self) -> bool:
        return all(result.accepted for result in self.results)
