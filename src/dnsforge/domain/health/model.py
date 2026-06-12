from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthCheck:
    name: str
    ok: bool
    detail: str = ""


@dataclass(frozen=True)
class HealthReport:
    checks: list[HealthCheck]

    @property
    def score(self) -> int:
        if not self.checks:
            return 0
        return int(sum(1 for c in self.checks if c.ok) * 100 / len(self.checks))

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.checks)

    def render(self) -> str:
        lines = ["CHECK\tSTATUS\tDETAIL"]
        for c in self.checks:
            lines.append(f"{c.name}\t{'OK' if c.ok else 'WARN'}\t{c.detail}")
        lines.append(f"Health Score\t{self.score}/100\t")
        return "\n".join(lines)
