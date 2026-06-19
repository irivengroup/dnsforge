from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ApiCapability:
    domain: str
    operation: str
    api: str


@dataclass(frozen=True)
class PublicApiContract:
    capabilities: tuple[ApiCapability, ...]


PUBLIC_API_CONTRACT = PublicApiContract(
    capabilities=(
        ApiCapability("zone", "create", "ZoneApi.create_zone"),
        ApiCapability("zone", "update", "ZoneApi.update_zone"),
        ApiCapability("zone", "delete", "ZoneApi.delete_zone"),
        ApiCapability("zone", "enable", "ZoneApi.enable_zone"),
        ApiCapability("zone", "disable", "ZoneApi.disable_zone"),
        ApiCapability("zone", "rollback", "ZoneApi.rollback_zone"),
        ApiCapability("catalog", "sync", "CatalogApi.sync"),
        ApiCapability("catalog", "repair", "CatalogApi.repair"),
        ApiCapability("cluster", "audit", "ClusterApi.audit_cluster"),
        ApiCapability("cluster", "sync", "ClusterApi.sync"),
        ApiCapability("dnssec", "enable", "DnssecApi.enable"),
        ApiCapability("dnssec", "disable", "DnssecApi.disable"),
        ApiCapability("dnssec", "rotate-ksk", "DnssecApi.rotate_ksk"),
        ApiCapability("dnssec", "rotate-zsk", "DnssecApi.rotate_zsk"),
        ApiCapability("migration", "migrate", "MigrationApi.migrate"),
        ApiCapability("disaster", "snapshot", "DisasterRecoveryApi.snapshot"),
        ApiCapability("disaster", "restore", "DisasterRecoveryApi.restore"),
        ApiCapability("disaster", "verify", "DisasterRecoveryApi.verify"),
    )
)
