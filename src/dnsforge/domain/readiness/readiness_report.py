from __future__ import annotations

from dataclasses import dataclass

from dnsforge.domain.readiness.readiness_result import ReadinessResult
from dnsforge.domain.readiness.readiness_status import ReadinessStatus


@dataclass(frozen=True)
class ReadinessReport:
    checks: list[ReadinessResult]

    @property
    def overall_status(self) -> ReadinessStatus:
        if any(check.status is ReadinessStatus.FAILED and check.critical for check in self.checks):
            return ReadinessStatus.FAILED
        if any(check.status is not ReadinessStatus.PASS for check in self.checks):
            return ReadinessStatus.WARNING
        return ReadinessStatus.PASS

    @property
    def overall_label(self) -> str:
        if self.overall_status is ReadinessStatus.PASS:
            return "READY"
        if self.overall_status is ReadinessStatus.WARNING:
            return "WARNING"
        return "FAILED"

    @property
    def score(self) -> int:
        if not self.checks:
            return 0
        weights = {ReadinessStatus.PASS: 100, ReadinessStatus.WARNING: 50, ReadinessStatus.FAILED: 0}
        return round(sum(weights[check.status] for check in self.checks) / len(self.checks))

    def as_dict(self) -> dict[str, object]:
        return {
            "overall_status": self.overall_label,
            "score": self.score,
            "checks": [check.as_dict() for check in self.checks],
        }

    def render(self) -> str:
        lines = [f"OVERALL STATUS : {self.overall_label}", ""]
        for check in self.checks:
            lines.append(f"[{check.status.value}] {check.name}: {check.message}")
        lines.extend(["", f"Score : {self.score}%"])
        return "\n".join(lines)
