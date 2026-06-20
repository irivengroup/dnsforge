from __future__ import annotations

import ipaddress
import re

from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.services.list_parser import ListParser
from dnsforge.shared.errors import SettingsError


class SettingsValidator:
    removed_network_aliases = (
        "FRONT_IP",
        "BACK_IP",
        "ADM_IP",
        "BIND_EXTERNAL_NICNAME",
        "BIND_EXTERNET_NICNAME",
    )

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

    def validate_nic_name_if_present(self, settings: dict[str, str], name: str) -> None:
        value = settings.get(name)
        if value is None:
            return
        value = value.strip().strip("\"'")
        if not value or value.lower() == "auto" or value.startswith("REPLACE_WITH_"):
            return
        if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,64}", value):
            raise SettingsError(f"{name} must be a valid network interface name: {value}")

    def reject_removed_network_aliases(self, settings: dict[str, str]) -> None:
        present = [name for name in self.removed_network_aliases if name in settings]
        if present:
            joined = ", ".join(present)
            raise SettingsError(
                f"removed legacy network aliases are not supported: {joined}; "
                "use BIND_EXTRANET_NICNAME, BIND_INTRANET_NICNAME and BIND_ADMIN_NICNAME"
            )

    def validate_address_list_if_present(self, settings: dict[str, str], name: str) -> None:
        if name not in settings:
            return
        values = self.list_parser.normalize(settings.get(name, ""))
        for value in values:
            try:
                ipaddress.ip_address(value.split("/", 1)[0])
            except ValueError as exc:
                raise SettingsError(f"{name} contains invalid address: {value}") from exc


class ProxySettingsValidator(SettingsValidator):
    def validate(self, settings: dict[str, str]) -> None:
        self.reject_removed_network_aliases(settings)
        if settings.get("ROLE") not in {"", None, "dns-proxy"}:
            raise SettingsError("ROLE must be dns-proxy")

        for name in (
            "BIND_EXTRANET_NICNAME",
            "BIND_INTRANET_NICNAME",
            "BIND_ADMIN_NICNAME",
        ):
            self.validate_nic_name_if_present(settings, name)

        for name in ("BIND_EXTRANET_IP", "BIND_INTRANET_IP", "BIND_ADMIN_IP"):
            if name in settings:
                self.validate_ipv4(settings, name)

        for name in ("ENABLE_RPZ", "ENABLE_RRL", "ENABLE_DNSSEC"):
            self.validate_bool_if_present(settings, name)

        self.validate_address_list_if_present(settings, "PEER_AUTHORITATIVE_ADDRESSES")
        self.validate_address_list_if_present(settings, "PEER_PROXY_ADDRESSES")

        legacy_proxy_names = (
            "AUTHORITATIVE_BACK_IP",
            "PROXY_VIP_FRONT_IP",
            "PROXY_KEEPALIVED_INTERFACE",
        )
        if any(name in settings for name in legacy_proxy_names):
            raise SettingsError(
                "legacy proxy HA variables are not supported; use PEER_AUTHORITATIVE_ADDRESSES and PEER_PROXY_ADDRESSES"
            )

        if settings.get("ENABLE_CLUSTER", "no") == "yes":
            raise SettingsError("cluster is supported only on authoritative servers")

        proxy_type = ProxyType.from_value(self.require(settings, "PROXY_TYPE"))

        if proxy_type is ProxyType.FORWARDER:
            for flag in (
                "ENABLE_PROXY_MASTER_ZONES",
                "ENABLE_PROXY_AUTHORITATIVE_ZONES",
                "ENABLE_PROXY_LOCAL_ZONES",
            ):
                if settings.get(flag, "no") == "yes":
                    raise SettingsError(f"FORWARDER mode does not allow {flag}=yes")


class AuthoritativeSettingsValidator(SettingsValidator):
    def validate(self, settings: dict[str, str]) -> None:
        self.reject_removed_network_aliases(settings)
        if settings.get("ROLE") not in {"", None, "dns-authoritative"}:
            raise SettingsError("ROLE must be dns-authoritative")

        for name in ("BIND_INTRANET_NICNAME", "BIND_ADMIN_NICNAME"):
            self.validate_nic_name_if_present(settings, name)

        for name in ("BIND_INTRANET_IP", "BIND_ADMIN_IP", "VIP_BACK_IP", "PEER_BACK_IP"):
            if name in settings:
                self.validate_ipv4(settings, name)

        if settings.get("ENABLE_RPZ", "no") == "yes":
            raise SettingsError("RPZ is not supported on authoritative servers")

        for name in ("ENABLE_RRL", "ENABLE_DNSSEC", "ENABLE_CLUSTER"):
            self.validate_bool_if_present(settings, name)

        self.validate_address_list_if_present(settings, "PEER_AUTHORITATIVE_ADDRESSES")
        self.validate_address_list_if_present(settings, "PEER_PROXY_ADDRESSES")
