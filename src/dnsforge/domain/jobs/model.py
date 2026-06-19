from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dnsforge.domain.events.model import utc_now


@dataclass(frozen=True)
class JobDefinition:
    job_id: str
    name: str
    command: list[str]
    description: str = ""
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class JobRun:
    run_id: str
    job_id: str
    status: str
    started_at: str = field(default_factory=utc_now)
    finished_at: str | None = None
    exit_code: int | None = None
    output: str = ""
