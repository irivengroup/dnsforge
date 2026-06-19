from __future__ import annotations

from enum import Enum


class ReadinessStatus(str, Enum):
    PASS = "PASS"  # nosec B105
    WARNING = "WARNING"
    FAILED = "FAILED"
