from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ChangeLifecycleStatus(str, Enum):
    DRAFT = "DRAFT"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    CANCELLED = "CANCELLED"


class ChangeTargetScope(str, Enum):
    SITE = "SITE"
    CLUSTER = "CLUSTER"
    AGENT = "AGENT"
    ZONE = "ZONE"
    CATALOG = "CATALOG"


class ChangeRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ChangeGateStatus(str, Enum):
    PASSED = "PASSED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class ChangeGate:
    name: str
    status: ChangeGateStatus
    message: str

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "status": self.status.value, "message": self.message}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> ChangeGate:
        return cls(
            name=str(data["name"]),
            status=ChangeGateStatus(str(data["status"])),
            message=str(data.get("message", "")),
        )


@dataclass(frozen=True)
class ChangeRequest:
    title: str
    description: str
    requested_by: str
    target_scope: ChangeTargetScope
    target_id: str
    operation: str
    payload: dict[str, Any]
    change_id: str = ""
    risk_level: ChangeRiskLevel = ChangeRiskLevel.LOW
    status: ChangeLifecycleStatus = ChangeLifecycleStatus.DRAFT
    reviewed_by: str | None = None
    approved_by: str | None = None
    scheduled_at: str | None = None
    failure_reason: str | None = None
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)

    @property
    def stable_hash(self) -> str:
        payload = {
            "title": self.title,
            "target_scope": self.target_scope.value,
            "target_id": self.target_id,
            "operation": self.operation,
            "payload": self.payload,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["target_scope"] = self.target_scope.value
        data["risk_level"] = self.risk_level.value
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> ChangeRequest:
        payload = data.get("payload", {})
        if not isinstance(payload, dict):
            raise ValueError("change payload must be a mapping")
        return cls(
            change_id=str(data.get("change_id", "")),
            title=str(data["title"]),
            description=str(data.get("description", "")),
            requested_by=str(data.get("requested_by", "system")),
            target_scope=ChangeTargetScope(str(data["target_scope"])),
            target_id=str(data["target_id"]),
            operation=str(data["operation"]),
            payload={str(key): value for key, value in payload.items()},
            risk_level=ChangeRiskLevel(str(data.get("risk_level", ChangeRiskLevel.LOW.value))),
            status=ChangeLifecycleStatus(str(data.get("status", ChangeLifecycleStatus.DRAFT.value))),
            reviewed_by=None if data.get("reviewed_by") is None else str(data.get("reviewed_by")),
            approved_by=None if data.get("approved_by") is None else str(data.get("approved_by")),
            scheduled_at=None if data.get("scheduled_at") is None else str(data.get("scheduled_at")),
            failure_reason=None if data.get("failure_reason") is None else str(data.get("failure_reason")),
            created_at=str(data.get("created_at", _utc_now())),
            updated_at=str(data.get("updated_at", _utc_now())),
        )


@dataclass(frozen=True)
class ChangePlan:
    change_id: str
    target_scope: ChangeTargetScope
    target_id: str
    risk_level: ChangeRiskLevel
    steps: tuple[str, ...]
    gates: tuple[ChangeGate, ...]
    plan_hash: str = ""

    def __post_init__(self) -> None:
        if not self.plan_hash:
            payload = {
                "change_id": self.change_id,
                "target_scope": self.target_scope.value,
                "target_id": self.target_id,
                "risk_level": self.risk_level.value,
                "steps": list(self.steps),
                "gates": [gate.to_dict() for gate in self.gates],
            }
            object.__setattr__(
                self,
                "plan_hash",
                hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest(),
            )

    @property
    def accepted(self) -> bool:
        return all(gate.status == ChangeGateStatus.PASSED for gate in self.gates)

    def to_dict(self) -> dict[str, object]:
        return {
            "change_id": self.change_id,
            "target_scope": self.target_scope.value,
            "target_id": self.target_id,
            "risk_level": self.risk_level.value,
            "steps": list(self.steps),
            "gates": [gate.to_dict() for gate in self.gates],
            "plan_hash": self.plan_hash,
            "accepted": self.accepted,
        }


@dataclass(frozen=True)
class ChangeApproval:
    change_id: str
    approver: str
    approved_at: str = field(default_factory=_utc_now)
    comment: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> ChangeApproval:
        return cls(
            change_id=str(data["change_id"]),
            approver=str(data["approver"]),
            approved_at=str(data.get("approved_at", _utc_now())),
            comment=str(data.get("comment", "")),
        )


@dataclass(frozen=True)
class ChangeExecution:
    change_id: str
    result: ChangeLifecycleStatus
    plan_hash: str
    targets: tuple[str, ...]
    started_at: str = field(default_factory=_utc_now)
    completed_at: str | None = None
    message: str = ""

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["result"] = self.result.value
        data["targets"] = list(self.targets)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> ChangeExecution:
        targets = data.get("targets", ())
        if not isinstance(targets, (list, tuple)):
            raise ValueError("execution targets must be a sequence")
        return cls(
            change_id=str(data["change_id"]),
            result=ChangeLifecycleStatus(str(data["result"])),
            plan_hash=str(data.get("plan_hash", "")),
            targets=tuple(str(target) for target in targets),
            started_at=str(data.get("started_at", _utc_now())),
            completed_at=None if data.get("completed_at") is None else str(data.get("completed_at")),
            message=str(data.get("message", "")),
        )


@dataclass(frozen=True)
class ChangeRollback:
    change_id: str
    reason: str
    triggered_by: str
    executed_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> ChangeRollback:
        return cls(
            change_id=str(data["change_id"]),
            reason=str(data.get("reason", "operator-request")),
            triggered_by=str(data.get("triggered_by", "system")),
            executed_at=str(data.get("executed_at", _utc_now())),
        )
