from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class DNSForgeOperation:
    operation: str
    payload: dict[str, object]


@dataclass(frozen=True)
class DNSForgeOperationResult:
    node_id: str
    accepted: bool
    message: str


class DNSForgeNodeClient(Protocol):
    def submit(self, node_id: str, operation: DNSForgeOperation) -> DNSForgeOperationResult:
        """Submit one operation to the DNSForge agent API on a managed node."""


class RecordingDNSForgeNodeClient:
    def __init__(self) -> None:
        self.operations: list[tuple[str, DNSForgeOperation]] = []

    def submit(self, node_id: str, operation: DNSForgeOperation) -> DNSForgeOperationResult:
        self.operations.append((node_id, operation))
        return DNSForgeOperationResult(node_id=node_id, accepted=True, message="queued")
