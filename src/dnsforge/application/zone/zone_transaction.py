from __future__ import annotations

from dataclasses import dataclass, field
from dnsforge.domain.zone.model import ZoneDefinition
from dnsforge.domain.zone.policy_validator import ServerProfile, ZonePolicyValidator
from dnsforge.infrastructure.catalog.zone_catalog import ZoneCatalog
from dnsforge.shared.errors import ZoneError


@dataclass
class ZoneChangePlan:
    """Atomic in-memory plan for zone catalog mutations.

    DNSForge zone operations often affect more than one zone: a forward A/AAAA
    change must create/update/delete the matching reverse PTR.  The plan keeps
    all intended changes in memory, validates the full resulting catalog, and
    commits once.  If persistence fails after the write starts, the previous
    catalog is restored.
    """

    original_zones: list[ZoneDefinition]
    profile: ServerProfile
    zones: list[ZoneDefinition] = field(init=False)
    changed_zones: set[str] = field(default_factory=set)
    deleted_zones: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.zones = list(self.original_zones)

    def list(self) -> list[ZoneDefinition]:
        return list(self.zones)

    def get(self, name: str) -> ZoneDefinition:
        for zone in self.zones:
            if zone.name == name:
                return zone
        raise ZoneError(f"zone not found: {name}")

    def exists(self, name: str) -> bool:
        return any(zone.name == name for zone in self.zones)

    def create(self, zone: ZoneDefinition) -> None:
        if self.exists(zone.name):
            raise ZoneError(f"zone already exists: {zone.name}")
        self._validate(zone)
        self.zones.append(zone)
        self.changed_zones.add(zone.name)
        self.deleted_zones.discard(zone.name)

    def update(self, zone: ZoneDefinition) -> None:
        self._validate(zone)
        updated: list[ZoneDefinition] = []
        found = False
        for current in self.zones:
            if current.name == zone.name:
                updated.append(zone)
                found = True
            else:
                updated.append(current)
        if not found:
            raise ZoneError(f"zone not found: {zone.name}")
        self.zones = updated
        self.changed_zones.add(zone.name)
        self.deleted_zones.discard(zone.name)

    def delete(self, name: str) -> None:
        if not self.exists(name):
            raise ZoneError(f"zone not found: {name}")
        self.zones = [zone for zone in self.zones if zone.name != name]
        self.changed_zones.discard(name)
        self.deleted_zones.add(name)

    def affected_zones(self) -> list[str]:
        return sorted(self.changed_zones | self.deleted_zones)

    def validate(self) -> None:
        seen: set[str] = set()
        for zone in self.zones:
            if zone.name in seen:
                raise ZoneError(f"duplicate zone in transaction: {zone.name}")
            seen.add(zone.name)
            self._validate(zone)

    def _validate(self, zone: ZoneDefinition) -> None:
        ZonePolicyValidator.validate_zone(zone, self.profile)


class ZoneTransactionEngine:
    """Commit ZoneChangePlan objects atomically to a ZoneCatalog."""

    def __init__(self, catalog: ZoneCatalog, profile: ServerProfile) -> None:
        self.catalog = catalog
        self.profile = profile

    def plan(self) -> ZoneChangePlan:
        return ZoneChangePlan(self.catalog.list(), self.profile)

    def commit(self, plan: ZoneChangePlan) -> None:
        plan.validate()
        previous = list(plan.original_zones)
        try:
            self.catalog.save(plan.list())
        except Exception:
            self.catalog.save(previous)
            raise
