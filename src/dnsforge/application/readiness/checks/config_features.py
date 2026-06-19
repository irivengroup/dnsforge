from __future__ import annotations

from collections.abc import Iterable

from dnsforge.domain.readiness import ReadinessResult, ReadinessStatus
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class SetupConfigurationFeatureCheck:
    """Readiness check for optional/operational DNSForge capabilities declared in setup.conf."""

    critical = False

    def __init__(self, paths: ProjectPaths, name: str, keywords: Iterable[str], success_message: str) -> None:
        self.paths = paths
        self.name = name
        self.keywords = tuple(keyword.upper() for keyword in keywords)
        self.success_message = success_message

    def run(self) -> ReadinessResult:
        if not self.paths.setup_file.exists():
            return ReadinessResult(
                self.name,
                ReadinessStatus.WARNING,
                "setup.conf is not available; capability cannot be evaluated",
                critical=self.critical,
            )
        content = self.paths.setup_file.read_text(encoding="utf-8", errors="ignore").upper()
        if any(keyword in content for keyword in self.keywords):
            return ReadinessResult(self.name, ReadinessStatus.PASS, self.success_message, critical=self.critical)
        return ReadinessResult(
            self.name,
            ReadinessStatus.WARNING,
            "capability is not explicitly configured in setup.conf",
            critical=self.critical,
        )


class AclConfigurationCheck(SetupConfigurationFeatureCheck):
    def __init__(self, paths: ProjectPaths) -> None:
        super().__init__(paths, "ACL Configuration", ("ACL", "ALLOW_QUERY", "TRUSTED_NETWORKS"), "ACLs are declared")


class ViewsConfigurationCheck(SetupConfigurationFeatureCheck):
    def __init__(self, paths: ProjectPaths) -> None:
        super().__init__(paths, "Views Configuration", ("VIEW", "INTERNAL", "EXTERNAL"), "views are declared")


class DnssecConfigurationCheck(SetupConfigurationFeatureCheck):
    def __init__(self, paths: ProjectPaths) -> None:
        super().__init__(paths, "DNSSEC Configuration", ("DNSSEC", "KSK", "ZSK"), "DNSSEC settings are declared")


class CatalogConfigurationCheck(SetupConfigurationFeatureCheck):
    def __init__(self, paths: ProjectPaths) -> None:
        super().__init__(paths, "Catalog Zones", ("CATALOG", "CATALOG_ZONE"), "catalog zone settings are declared")


class ClusterConfigurationCheck(SetupConfigurationFeatureCheck):
    def __init__(self, paths: ProjectPaths) -> None:
        super().__init__(
            paths,
            "Cluster Configuration",
            ("CLUSTER", "PEER_AUTHORITATIVE", "PEER_PROXY"),
            "cluster peers are declared",
        )
