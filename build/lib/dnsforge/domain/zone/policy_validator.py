from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from dnsforge.domain.zone.model import ZoneDefinition, ZoneType
from dnsforge.domain.zone.reverse import is_reverse_zone_name
from dnsforge.shared.errors import ZoneError


class ZoneScope(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"

    @classmethod
    def from_value(cls, value: str) -> "ZoneScope":
        normalized = value.strip().lower()
        for item in cls:
            if item.value == normalized:
                return item
        raise ZoneError(f"unsupported zone scope: {value}")


class ServerProfile(str, Enum):
    AUTHORITATIVE = "authoritative"
    PROXY_FORWARDER = "proxy-forwarder"
    PROXY_HYBRID = "proxy-hybrid"

    @classmethod
    def from_value(cls, value: str) -> "ServerProfile":
        normalized = value.strip().lower()
        for item in cls:
            if item.value == normalized:
                return item
        raise ZoneError(f"unsupported server profile: {value}")


@dataclass(frozen=True)
class ZonePolicyKey:
    profile: ServerProfile
    scope: ZoneScope
    zone_type: ZoneType


class ZonePolicyValidator:
    """Enterprise DNSForge zone compatibility matrix.

    The validator is intentionally domain-level: every CLI/API/import path must
    validate a zone before it can be persisted or rendered. It prevents BIND
    configurations that are syntactically possible but operationally incoherent
    for a DNSForge node profile.
    """

    ALLOWED: dict[tuple[ServerProfile, ZoneScope], frozenset[ZoneType]] = {
        (ServerProfile.AUTHORITATIVE, ZoneScope.INTERNAL): frozenset(
            {
                ZoneType.MASTER,
                ZoneType.SECONDARY,
                ZoneType.STUB,
                ZoneType.FORWARD,
                ZoneType.RPZ,
                ZoneType.CATALOG,
                ZoneType.REVERSE_MASTER,
                ZoneType.REVERSE_SECONDARY,
            }
        ),
        (ServerProfile.AUTHORITATIVE, ZoneScope.EXTERNAL): frozenset(
            {
                ZoneType.MASTER,
                ZoneType.SECONDARY,
                ZoneType.STUB,
                ZoneType.CATALOG,
                ZoneType.REVERSE_MASTER,
                ZoneType.REVERSE_SECONDARY,
            }
        ),
        (ServerProfile.PROXY_FORWARDER, ZoneScope.INTERNAL): frozenset({ZoneType.FORWARD, ZoneType.HINT, ZoneType.RPZ}),
        (ServerProfile.PROXY_FORWARDER, ZoneScope.EXTERNAL): frozenset({ZoneType.FORWARD, ZoneType.HINT}),
        (ServerProfile.PROXY_HYBRID, ZoneScope.INTERNAL): frozenset(
            {
                ZoneType.MASTER,
                ZoneType.SECONDARY,
                ZoneType.STUB,
                ZoneType.FORWARD,
                ZoneType.HINT,
                ZoneType.RPZ,
                ZoneType.CATALOG,
                ZoneType.REVERSE_MASTER,
                ZoneType.REVERSE_SECONDARY,
            }
        ),
        (ServerProfile.PROXY_HYBRID, ZoneScope.EXTERNAL): frozenset(
            {
                ZoneType.MASTER,
                ZoneType.SECONDARY,
                ZoneType.STUB,
                ZoneType.CATALOG,
                ZoneType.REVERSE_MASTER,
                ZoneType.REVERSE_SECONDARY,
            }
        ),
    }

    @classmethod
    def allowed_types(cls, profile: ServerProfile, scope: ZoneScope) -> frozenset[ZoneType]:
        return cls.ALLOWED[(profile, scope)]

    @classmethod
    def is_allowed(cls, profile: ServerProfile, scope: ZoneScope, zone_type: ZoneType) -> bool:
        return zone_type in cls.allowed_types(profile, scope)

    @classmethod
    def validate_key(cls, key: ZonePolicyKey) -> None:
        if not cls.is_allowed(key.profile, key.scope, key.zone_type):
            allowed = ", ".join(sorted(item.value for item in cls.allowed_types(key.profile, key.scope)))
            raise ZoneError(
                f"zone type {key.zone_type.value!r} is not allowed for "
                f"profile={key.profile.value} scope={key.scope.value}; allowed: {allowed}"
            )

    @classmethod
    def validate_zone(cls, zone: ZoneDefinition, profile: ServerProfile) -> None:
        zone.validate()
        for view in zone.views:
            scope = ZoneScope.from_value(view)
            key = ZonePolicyKey(profile, scope, zone.zone_type)
            cls.validate_key(key)
            cls._validate_reverse_name(zone, key)
            cls._validate_special_zone_name(zone, key)

    @staticmethod
    def _validate_reverse_name(zone: ZoneDefinition, key: ZonePolicyKey) -> None:
        if key.zone_type in {ZoneType.REVERSE_MASTER, ZoneType.REVERSE_SECONDARY} and not is_reverse_zone_name(
            zone.name
        ):
            raise ZoneError(f"reverse zone type requires an in-addr.arpa or ip6.arpa name: {zone.name}")
        if is_reverse_zone_name(zone.name) and key.zone_type in {ZoneType.MASTER, ZoneType.SECONDARY}:
            raise ZoneError(f"reverse zone {zone.name} must use reverse-master or reverse-secondary")

    @staticmethod
    def _validate_special_zone_name(zone: ZoneDefinition, key: ZonePolicyKey) -> None:
        if key.zone_type is ZoneType.RPZ and not (zone.name.startswith("rpz.") or zone.name.endswith(".rpz")):
            raise ZoneError("RPZ zones must use an rpz-prefixed or rpz-suffixed zone name")
        if key.zone_type is ZoneType.HINT and zone.name != ".":
            raise ZoneError("hint zones must use the root zone name '.'")
