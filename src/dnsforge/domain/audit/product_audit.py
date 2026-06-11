from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AuditFinding:
    severity: str
    message: str
    path: Path | None = None


@dataclass
class ProductAuditReport:
    findings: list[AuditFinding]

    @property
    def ok(self) -> bool:
        return not any(finding.severity == "error" for finding in self.findings)

    def add_error(self, message: str, path: Path | None = None) -> None:
        self.findings.append(AuditFinding("error", message, path))

    def render(self) -> str:
        if not self.findings:
            return "Product audit OK"
        return "\n".join(
            f"{finding.severity.upper()}: {finding.message}"
            + (f" [{finding.path}]" if finding.path else "")
            for finding in self.findings
        )
