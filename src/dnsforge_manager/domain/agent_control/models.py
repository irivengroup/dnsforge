from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class AgentApiAction(str, Enum):
    INITIALIZE = "initialize"
    VALIDATE = "validate"
    DOCTOR = "doctor"
    STATUS = "status"
    ZONE = "zone"
    CATALOG = "catalog"
    DNSSEC = "dnssec"
    BACKUP = "backup"
    RESTORE = "restore"
    CONFIG = "config"
    NETWORK = "network"


@dataclass(frozen=True)
class AgentApiTarget:
    node_id: str
    api_endpoint: str
    fingerprint: str = ""
    site: str = "default"
    cluster: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class AgentApiCommand:
    action: AgentApiAction
    operation: str
    payload: dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid4()))
    idempotency_key: str = field(default_factory=lambda: str(uuid4()))
    timeout_seconds: float = 30.0

    @classmethod
    def from_payload(cls, data: dict[str, Any]) -> "AgentApiCommand":
        payload = data.get("payload", {})
        if not isinstance(payload, dict):
            raise ValueError("agent API command payload must be a JSON object")
        return cls(
            action=AgentApiAction(str(data["action"])),
            operation=str(data.get("operation", data["action"])),
            payload={str(key): value for key, value in payload.items()},
            request_id=str(data.get("request_id") or uuid4()),
            idempotency_key=str(data.get("idempotency_key") or uuid4()),
            timeout_seconds=float(data.get("timeout_seconds", 30.0)),
        )

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["action"] = self.action.value
        return result


@dataclass(frozen=True)
class AgentApiResult:
    node_id: str
    action: str
    operation: str
    accepted: bool
    status_code: int
    message: str
    request_id: str
    response: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
