from __future__ import annotations

from pathlib import Path

from dnsforge.application.cluster.cluster_service import ClusterService
from dnsforge.application.disaster.disaster_service import DisasterRecoveryService
from dnsforge.application.zone.zone_manager import ZoneManager
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class DnsForgeApplicationApi:
    """Internal application facade prepared for DNSForge Manager/REST adapters."""

    def __init__(self, paths: ProjectPaths | None = None) -> None:
        self.paths = paths or ProjectPaths()

    def audit_zone(self, zone: str) -> str:
        ok, report = ZoneManager(self.paths).audit_zone(zone)
        if not ok:
            return report
        return report

    def audit_cluster(self, setup_file: Path) -> str:
        ok, report = ClusterService().audit(setup_file)
        if not ok:
            return report
        return report

    def disaster_snapshot(self, reason: str) -> str:
        return DisasterRecoveryService(self.paths).snapshot(reason)
