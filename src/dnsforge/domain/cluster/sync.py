from __future__ import annotations

from dataclasses import dataclass, field
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
