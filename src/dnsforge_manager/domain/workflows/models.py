from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ChangeRequestStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass(frozen=True)
class ManagerChangeRequest:
    cluster_id: str
    operation: str
    payload: dict[str, object]
    change_id: str = ""
    status: ChangeRequestStatus = ChangeRequestStatus.DRAFT
    created_by: str = "system"
    approved_by: str | None = None
    plan_hash: str | None = None
    rollback_plan_hash: str | None = None
    failure_reason: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def stable_hash(self) -> str:
        payload = {
            "cluster_id": self.cluster_id,
            "operation": self.operation,
            "payload": self.payload,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> ManagerChangeRequest:
        raw = dict(data)
        status = ChangeRequestStatus(str(raw.pop("status", ChangeRequestStatus.DRAFT.value)))
        payload = raw.pop("payload", {})
        if not isinstance(payload, dict):
            raise ValueError("change payload must be a mapping")
        return cls(
            cluster_id=str(raw.pop("cluster_id")),
            operation=str(raw.pop("operation")),
            payload={str(key): value for key, value in payload.items()},
            change_id=str(raw.pop("change_id", "")),
            status=status,
            created_by=str(raw.pop("created_by", "system")),
            approved_by=None if raw.get("approved_by") is None else str(raw.pop("approved_by")),
            plan_hash=None if raw.get("plan_hash") is None else str(raw.pop("plan_hash")),
            rollback_plan_hash=None if raw.get("rollback_plan_hash") is None else str(raw.pop("rollback_plan_hash")),
            failure_reason=None if raw.get("failure_reason") is None else str(raw.pop("failure_reason")),
            created_at=str(raw.pop("created_at", datetime.now(timezone.utc).isoformat())),
            updated_at=str(raw.pop("updated_at", datetime.now(timezone.utc).isoformat())),
        )
