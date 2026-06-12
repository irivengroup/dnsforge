from __future__ import annotations

import pytest

from dnsforge.domain.zone.model import ZoneDefinition, ZoneType
from dnsforge.domain.zone.policy_validator import ServerProfile, ZonePolicyValidator
from dnsforge.shared.errors import ZoneError


def test_proxy_forwarder_rejects_authoritative_master_zone() -> None:
    zone = ZoneDefinition("example.com", ZoneType.MASTER, ["internal"])

    with pytest.raises(ZoneError, match="not allowed"):
        ZonePolicyValidator.validate_zone(zone, ServerProfile.PROXY_FORWARDER)


def test_external_rpz_is_rejected() -> None:
    zone = ZoneDefinition("rpz.local", ZoneType.RPZ, ["external"])

    with pytest.raises(ZoneError, match="not allowed"):
        ZonePolicyValidator.validate_zone(zone, ServerProfile.AUTHORITATIVE)


def test_hint_zone_must_be_root() -> None:
    zone = ZoneDefinition("corp.local", ZoneType.HINT, ["internal"])

    with pytest.raises(ZoneError, match="root zone"):
        ZonePolicyValidator.validate_zone(zone, ServerProfile.PROXY_FORWARDER)


def test_reverse_zone_must_use_reverse_type() -> None:
    zone = ZoneDefinition("10.168.192.in-addr.arpa", ZoneType.MASTER, ["internal"])

    with pytest.raises(ZoneError, match="must use reverse-master"):
        ZonePolicyValidator.validate_zone(zone, ServerProfile.AUTHORITATIVE)


def test_internal_authoritative_reverse_master_is_allowed() -> None:
    zone = ZoneDefinition("10.168.192.in-addr.arpa", ZoneType.REVERSE_MASTER, ["internal"])

    ZonePolicyValidator.validate_zone(zone, ServerProfile.AUTHORITATIVE)
