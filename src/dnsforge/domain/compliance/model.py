from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class ComplianceStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    WARNING = "WARNING"
    DRIFTED = "DRIFTED"
    FAILED = "FAILED"


class DriftSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class ConfigurationBaseline:
    profile: str
    bind_layout: str
    resources: tuple[str, ...]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ConfigurationFingerprint:
    scope: str
    sha256: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ConfigurationDrift:
    resource: str
    expected_hash: Optional[str]
    actual_hash: Optional[str]
    severity: DriftSeverity

    def title(self) -> str:
        return f"{self.severity.value}\t{self.resource}"


@dataclass(frozen=True)
class ConfigurationCompliance:
    status: ComplianceStatus
    fingerprint: Optional[ConfigurationFingerprint]
    drifts: tuple[ConfigurationDrift, ...]

    @property
    def is_compliant(self) -> bool:
        return self.status is ComplianceStatus.COMPLIANT


@dataclass(frozen=True)
class ConfigurationRepairPlan:
    resources_to_restore: tuple[str, ...]
    resources_to_regenerate: tuple[str, ...]
    requires_reload: bool = False
    requires_restart: bool = False

    @property
    def is_empty(self) -> bool:
        return not self.resources_to_restore and not self.resources_to_regenerate
