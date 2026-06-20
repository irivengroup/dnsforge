from __future__ import annotations

import pytest

from dnsforge.domain.services.settings_validator import AuthoritativeSettingsValidator, ProxySettingsValidator
from dnsforge.shared.errors import SettingsError


def _proxy_settings(**extra: str) -> dict[str, str]:
    settings = {
        "ROLE": "dns-proxy",
        "PROXY_TYPE": "hybrid",
        "ENABLE_CLUSTER": "no",
        "ENABLE_RPZ": "yes",
        "ENABLE_RRL": "yes",
        "ENABLE_DNSSEC": "no",
        "BIND_EXTRANET_NICNAME": "eth2",
        "BIND_INTRANET_NICNAME": "eth1",
        "BIND_ADMIN_NICNAME": "eth0",
    }
    settings.update(extra)
    return settings


def _authoritative_settings(**extra: str) -> dict[str, str]:
    settings = {
        "ROLE": "dns-authoritative",
        "ENABLE_RPZ": "no",
        "ENABLE_RRL": "yes",
        "ENABLE_DNSSEC": "yes",
        "ENABLE_CLUSTER": "yes",
        "BIND_INTRANET_NICNAME": "eth1",
        "BIND_ADMIN_NICNAME": "eth0",
    }
    settings.update(extra)
    return settings


@pytest.mark.parametrize(
    "name",
    [
        "FRONT_IP",
        "BACK_IP",
        "ADM_IP",
        "BIND_EXTERNAL_NICNAME",
        "BIND_EXTERNET_NICNAME",
    ],
)
def test_proxy_validator_rejects_removed_network_aliases(name: str) -> None:
    with pytest.raises(SettingsError, match="removed legacy network aliases"):
        ProxySettingsValidator().validate(_proxy_settings(**{name: "eth9"}))


@pytest.mark.parametrize(
    "name",
    [
        "FRONT_IP",
        "BACK_IP",
        "ADM_IP",
        "BIND_EXTERNAL_NICNAME",
        "BIND_EXTERNET_NICNAME",
    ],
)
def test_authoritative_validator_rejects_removed_network_aliases(name: str) -> None:
    with pytest.raises(SettingsError, match="removed legacy network aliases"):
        AuthoritativeSettingsValidator().validate(_authoritative_settings(**{name: "eth9"}))
