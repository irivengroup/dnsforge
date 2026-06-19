from __future__ import annotations

from pathlib import Path

from dnsforge.api.catalog import CatalogApi
from dnsforge.api.cluster import ClusterApi
from dnsforge.api.disaster import DisasterRecoveryApi
from dnsforge.api.dnssec import DnssecApi
from dnsforge.api.zones import ZoneApi
from dnsforge.application.events.event_bus import EventBus
from dnsforge.infrastructure.audit.event_repository import AuditEventRepository
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class DnsForgeApplicationApi:
    """Stable internal facade prepared for DNSForge Manager, REST adapters and automation."""

    def __init__(self, paths: ProjectPaths | None = None, event_bus: EventBus | None = None) -> None:
        self.paths = paths or ProjectPaths()
        self.event_bus = event_bus or EventBus()
        self.audit_repository = AuditEventRepository(self.paths.settings_root / "audit-events.jsonl")
        self.zones = ZoneApi(self.paths, self.event_bus, self.audit_repository)
        self.catalog = CatalogApi(self.paths, self.event_bus, self.audit_repository)
        self.disaster = DisasterRecoveryApi(self.paths, self.event_bus, self.audit_repository)

    def dnssec(self, setup_file: Path) -> DnssecApi:
        return DnssecApi(setup_file, self.event_bus, self.audit_repository)

    def cluster(self, setup_file: Path) -> ClusterApi:
        return ClusterApi(setup_file, self.event_bus, self.audit_repository)

    def audit_zone(self, zone: str) -> str:
        ok, report = self.zones.manager.audit_zone(zone)
        return report

    def audit_cluster(self, setup_file: Path) -> str:
        ok, report = self.cluster(setup_file).audit_cluster()
        return report

    def disaster_snapshot(self, reason: str) -> str:
        return self.disaster.snapshot(reason)
