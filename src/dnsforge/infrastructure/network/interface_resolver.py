from __future__ import annotations

import fcntl
import ipaddress
import socket
import struct
from dataclasses import dataclass
from pathlib import Path

from dnsforge.domain.network.interfaces import BindInterfaceSelection, ResolvedBindInterfaces
from dnsforge.shared.errors import SettingsError


SIOCGIFADDR = 0x8915
PROC_NET_ROUTE = Path("/proc/net/route")
SYS_CLASS_NET = Path("/sys/class/net")


def _clean(value: str | None) -> str:
    value = (value or "").strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return value.strip()


@dataclass(frozen=True)
class InterfaceAddressResolver:
    """Resolve setup.conf NIC names into IPv4 addresses for BIND rendering."""

    def default_admin_interface(self) -> str:
        route_interface = self._default_route_interface()
        if route_interface:
            return route_interface
        return "lo"

    def selection_from_settings(self, settings: dict[str, str]) -> BindInterfaceSelection:
        admin = _clean(settings.get("BIND_ADMIN_NICNAME")) or self.default_admin_interface()
        external = (
            _clean(settings.get("BIND_EXTRANET_NICNAME"))
            or _clean(settings.get("BIND_EXTERNAL_NICNAME"))
            or _clean(settings.get("BIND_EXTERNET_NICNAME"))
            or admin
        )
        intranet = _clean(settings.get("BIND_INTRANET_NICNAME")) or admin
        return BindInterfaceSelection(
            external_nic=external,
            intranet_nic=intranet,
            admin_nic=admin,
        )

    def resolve(self, settings: dict[str, str]) -> ResolvedBindInterfaces:
        selection = self.selection_from_settings(settings)
        return ResolvedBindInterfaces(
            external_ip=self._resolve_named_or_legacy(
                settings,
                selection.external_nic,
                "FRONT_IP",
                "BIND_EXTRANET_NICNAME",
                "BIND_EXTERNAL_NICNAME",
                "BIND_EXTERNET_NICNAME",
            ),
            intranet_ip=self._resolve_named_or_legacy(
                settings,
                selection.intranet_nic,
                "BACK_IP",
                "BIND_INTRANET_NICNAME",
            ),
            admin_ip=self._resolve_named_or_legacy(
                settings,
                selection.admin_nic,
                "ADM_IP",
                "BIND_ADMIN_NICNAME",
            ),
        )

    def enrich_settings(self, settings: dict[str, str]) -> dict[str, str]:
        enriched = dict(settings)
        resolved = self.resolve(enriched)
        enriched.setdefault("FRONT_IP", resolved.external_ip)
        enriched.setdefault("BACK_IP", resolved.intranet_ip)
        enriched.setdefault("ADM_IP", resolved.admin_ip)
        enriched.setdefault("DNS_LISTEN_ON", "; ".join(resolved.distinct_ips()) + ";")
        enriched.setdefault(
            "BIND_ADMIN_LISTEN_ON",
            "; ".join(["127.0.0.1", resolved.admin_ip]) + ";",
        )
        return enriched

    def _resolve_named_or_legacy(
        self,
        settings: dict[str, str],
        nic_name: str,
        legacy_key: str,
        *nic_keys: str,
    ) -> str:
        explicit_nic = any(_clean(settings.get(key)) for key in nic_keys)
        if explicit_nic and nic_name.upper() not in {
            "AUTO",
            "REPLACE_WITH_FRONT_NICNAME",
            "REPLACE_WITH_BACK_NICNAME",
            "REPLACE_WITH_ADM_NICNAME",
        }:
            return self.ipv4_for_interface(nic_name)
        legacy = _clean(settings.get(legacy_key))
        if legacy and not legacy.startswith("REPLACE_"):
            self._validate_ipv4(legacy, legacy_key)
            return legacy
        admin = self.default_admin_interface()
        return self.ipv4_for_interface(admin)

    def ipv4_for_interface(self, nic_name: str) -> str:
        if nic_name == "lo":
            return "127.0.0.1"
        self._validate_interface_name(nic_name)
        try:
            ifname = nic_name.encode("utf-8")[:15]
            request = struct.pack("256s", ifname)
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                response = fcntl.ioctl(sock.fileno(), SIOCGIFADDR, request)
            value = socket.inet_ntoa(response[20:24])
            self._validate_ipv4(value, nic_name)
            return value
        except OSError as exc:
            raise SettingsError(f"cannot resolve IPv4 address for interface {nic_name!r}") from exc

    def _default_route_interface(self) -> str:
        try:
            lines = PROC_NET_ROUTE.read_text(encoding="utf-8").splitlines()
        except OSError:
            lines = []
        for line in lines[1:]:
            fields = line.split()
            if len(fields) >= 2 and fields[1] == "00000000":
                return fields[0]
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect(("1.1.1.1", 53))
                local_ip = sock.getsockname()[0]
            return self._interface_for_ip(local_ip) or "lo"
        except OSError:
            return "lo"

    def _interface_for_ip(self, ip_value: str) -> str | None:
        for interface_path in self._iter_interfaces():
            name = interface_path.name
            try:
                if self.ipv4_for_interface(name) == ip_value:
                    return name
            except SettingsError:
                continue
        return None

    def _iter_interfaces(self) -> tuple[Path, ...]:
        try:
            return tuple(path for path in SYS_CLASS_NET.iterdir() if path.is_dir())
        except OSError:
            return ()

    def _validate_interface_name(self, nic_name: str) -> None:
        invalid = not nic_name or "/" in nic_name or "\x00" in nic_name or len(nic_name.encode()) > 15
        if invalid:
            raise SettingsError(f"invalid interface name: {nic_name!r}")

    def _validate_ipv4(self, value: str, name: str) -> None:
        try:
            ipaddress.IPv4Address(value.split("/", 1)[0])
        except ValueError as exc:
            raise SettingsError(f"{name} must resolve to a valid IPv4 address: {value}") from exc
