from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from enum import Enum


class ClusterDriftSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ClusterPeerState:
    address: str
    reachable: bool
    zone_count: int = 0
    catalog_serial: str = "unknown"
    dnssec_state: str = "unknown"
    manifest_checksum: str = "unknown"
    zone_checksum: str = "unknown"
    soa_serials_checksum: str = "unknown"
    message: str = ""


@dataclass(frozen=True)
class ClusterDrift:
    severity: ClusterDriftSeverity
    peer: str
    area: str
    message: str


@dataclass(frozen=True)
class ClusterSyncPlan:
    local_node: str
    peers: list[str]
    zones: list[str]
    files: list[str]
    dry_run: bool
    file_checksums: dict[str, str] = field(default_factory=dict)
    zone_checksum: str = ""
    soa_serials: dict[str, int] = field(default_factory=dict)
    soa_serials_checksum: str = ""
    manifest_checksum: str = ""

    @property
    def target_count(self) -> int:
        return len(self.peers)

    @property
    def zone_count(self) -> int:
        return len(self.zones)


@dataclass(frozen=True)
class ClusterAuditFinding:
    severity: ClusterDriftSeverity
    area: str
    target: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity.value,
            "area": self.area,
            "target": self.target,
            "message": self.message,
        }


@dataclass(frozen=True)
class ClusterAuditReport:
    ok: bool
    local_node: str
    peer_count: int
    zone_count: int
    manifest_checksum: str
    zone_checksum: str
    soa_serials_checksum: str
    findings: list[ClusterAuditFinding] = field(default_factory=list)

    @property
    def highest_severity(self) -> str:
        if any(f.severity is ClusterDriftSeverity.CRITICAL for f in self.findings):
            return ClusterDriftSeverity.CRITICAL.value
        if any(f.severity is ClusterDriftSeverity.WARNING for f in self.findings):
            return ClusterDriftSeverity.WARNING.value
        return ClusterDriftSeverity.INFO.value

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "highest_severity": self.highest_severity,
            "local_node": self.local_node,
            "peer_count": self.peer_count,
            "zone_count": self.zone_count,
            "manifest_checksum": self.manifest_checksum,
            "zone_checksum": self.zone_checksum,
            "soa_serials_checksum": self.soa_serials_checksum,
            "findings": [finding.to_dict() for finding in self.findings],
        }
