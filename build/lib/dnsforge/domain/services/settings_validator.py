from __future__ import annotations

import ipaddress

from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.services.list_parser import ListParser
from dnsforge.shared.errors import SettingsError


class SettingsValidator:
    def __init__(self, list_parser: ListParser | None = None) -> None:
        self.list_parser = list_parser or ListParser()

    def require(self, settings: dict[str, str], name: str) -> str:
        value = settings.get(name, "")
        if not value:
            raise SettingsError(f"missing required setting: {name}")
        if "CHANGE_ME" in value or "REPLACE_" in value:
            raise SettingsError(f"{name} contains placeholder")
        return value

    def validate_ipv4(self, settings: dict[str, str], name: str) -> None:
        value = self.require(settings, name)
        try:
            ipaddress.IPv4Address(value.split("/", 1)[0])
        except ValueError as exc:
            raise SettingsError(f"{name} must be a valid IPv4 address: {value}") from exc

    def validate_bool_if_present(self, settings: dict[str, str], name: str) -> None:
        value = settings.get(name)
        if value is not None and value not in {"yes", "no"}:
            raise SettingsError(f"{name} must be yes or no")


class ProxySettingsValidator(SettingsValidator):
    def validate(self, settings: dict[str, str]) -> None:
        if settings.get("ROLE") not in {"", None, "dns-proxy"}:
            raise SettingsError("ROLE must be dns-proxy")

        for name in ("FRONT_IP", "BACK_IP", "ADM_IP"):
            if name in settings:
                self.validate_ipv4(settings, name)

        for name in ("ENABLE_RPZ", "ENABLE_RRL", "ENABLE_DNSSEC", "ENABLE_PROXY_HA"):
            self.validate_bool_if_present(settings, name)

        proxy_type = ProxyType.from_value(self.require(settings, "PROXY_TYPE"))

        if proxy_type is ProxyType.FORWARDER:
            for flag in ("ENABLE_PROXY_MASTER_ZONES", "ENABLE_PROXY_AUTHORITATIVE_ZONES", "ENABLE_PROXY_LOCAL_ZONES"):
                if settings.get(flag, "no") == "yes":
                    raise SettingsError(f"FORWARDER mode does not allow {flag}=yes")


class AuthoritativeSettingsValidator(SettingsValidator):
    def validate(self, settings: dict[str, str]) -> None:
        if settings.get("ROLE") not in {"", None, "dns-authoritative"}:
            raise SettingsError("ROLE must be dns-authoritative")

        for name in ("BACK_IP", "ADM_IP", "VIP_BACK_IP", "PEER_BACK_IP"):
            if name in settings:
                self.validate_ipv4(settings, name)

        if settings.get("ENABLE_RPZ", "no") == "yes":
            raise SettingsError("RPZ is not supported on authoritative servers")

        for name in ("ENABLE_RRL", "ENABLE_DNSSEC"):
            self.validate_bool_if_present(settings, name)
