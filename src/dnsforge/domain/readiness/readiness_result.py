from __future__ import annotations

from dataclasses import dataclass

from dnsforge.domain.readiness.readiness_status import ReadinessStatus


@dataclass(frozen=True)
class ReadinessResult:
    name: str
    status: ReadinessStatus
    message: str
    critical: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "critical": self.critical,
        }
