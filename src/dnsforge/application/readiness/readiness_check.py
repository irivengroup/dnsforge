from __future__ import annotations

from typing import Protocol

from dnsforge.domain.readiness import ReadinessResult


class ReadinessCheck(Protocol):
    name: str
    critical: bool

    def run(self) -> ReadinessResult: ...
