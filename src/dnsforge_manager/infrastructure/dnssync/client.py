from __future__ import annotations

from typing import Protocol

from dnsforge_manager.domain.dnssync.models import DNSForgeOperation, DNSForgeOperationResult


class DNSForgeNodeClient(Protocol):
    def submit(self, node_id: str, operation: DNSForgeOperation) -> DNSForgeOperationResult:
        """Submit one operation to the DNSForge agent API on a managed node."""
        ...

    def readiness(self, node_id: str) -> dict[str, object]:
        """Return the operational readiness reported by one DNSForge agent."""
        ...


class RecordingDNSForgeNodeClient:
    def __init__(self) -> None:
        self.operations: list[tuple[str, DNSForgeOperation]] = []

    def submit(self, node_id: str, operation: DNSForgeOperation) -> DNSForgeOperationResult:
        self.operations.append((node_id, operation))
        return DNSForgeOperationResult(node_id=node_id, accepted=True, message="queued")

    def readiness(self, node_id: str) -> dict[str, object]:
        return {
            "node_id": node_id,
            "status": "READY",
            "score": 100,
            "checks": [
                {
                    "name": "Agent Readiness",
                    "status": "PASS",
                    "message": "recording client reports agent ready",
                    "critical": True,
                }
            ],
        }
