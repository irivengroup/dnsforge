from __future__ import annotations

from pathlib import Path

from dnsforge.domain.zone.policy_validator import ServerProfile, ZonePolicyValidator, ZoneScope
from dnsforge.domain.zone.template_registry import ZoneTemplateRegistry
from dnsforge.domain.zone.model import ZoneType

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESOURCE_ROOT = PROJECT_ROOT / "src/dnsforge/infrastructure/bind/resources"


def test_zone_template_registry_matches_policy_matrix() -> None:
    registered = {(item.key.profile, item.key.scope, item.key.zone_type) for item in ZoneTemplateRegistry.artifacts()}
    expected = {
        (profile, scope, zone_type)
        for profile in ServerProfile
        for scope in ZoneScope
        for zone_type in ZonePolicyValidator.allowed_types(profile, scope)
    }

    assert registered == expected


def test_all_zone_template_registry_files_exist() -> None:
    for artifact in ZoneTemplateRegistry.artifacts():
        assert (RESOURCE_ROOT / artifact.template).is_file(), artifact.template


def test_proxy_forwarder_has_no_authoritative_zone_templates_rendered() -> None:
    rendered_types = {
        artifact.key.zone_type
        for artifact in ZoneTemplateRegistry.artifacts()
        if artifact.key.profile is ServerProfile.PROXY_FORWARDER and artifact.key.scope is ZoneScope.INTERNAL
    }

    assert ZoneType.MASTER not in rendered_types
    assert ZoneType.SECONDARY not in rendered_types
    assert {ZoneType.FORWARD, ZoneType.HINT, ZoneType.RPZ}.issubset(rendered_types)
