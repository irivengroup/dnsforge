from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ManagerChangeRequest:
    cluster_id: str
    operation: str
    payload: dict[str, object]
