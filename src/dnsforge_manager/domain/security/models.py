from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AgentTrustState(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REVOKED = "revoked"


@dataclass(frozen=True)
class NodeApprovalDecision:
    node_id: str
    approved: bool
    fingerprint: str | None = None
    message: str = ""
