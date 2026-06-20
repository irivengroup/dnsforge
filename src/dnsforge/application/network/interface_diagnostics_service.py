from __future__ import annotations

import json
from pathlib import Path

from dnsforge.infrastructure.network.interface_resolver import InterfaceAddressResolver
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader


class InterfaceDiagnosticsService:
    """Preview DNSForge NIC-to-IP resolution before BIND rendering or initialize."""

    def __init__(
        self,
        setup_file: Path,
        resolver: InterfaceAddressResolver | None = None,
        loader: EnvSettingsLoader | None = None,
    ) -> None:
        self.setup_file = setup_file
        self.resolver = resolver or InterfaceAddressResolver()
        self.loader = loader or EnvSettingsLoader()

    def as_dict(self) -> dict[str, object]:
        settings = self.loader.load(self.setup_file)
        report = self.resolver.resolution_report(settings)
        enriched = self.resolver.enrich_settings(settings)
        distinct_ips = [item.strip() for item in enriched["DNS_LISTEN_ON"].split(";") if item.strip()]
        admin_ips = [item.strip() for item in enriched["BIND_ADMIN_LISTEN_ON"].split(";") if item.strip()]
        return {
            "setup_file": str(self.setup_file),
            "interfaces": {
                "extranet": {"nic": report.external_nic, "ip": report.external_ip},
                "intranet": {"nic": report.intranet_nic, "ip": report.intranet_ip},
                "admin": {"nic": report.admin_nic, "ip": report.admin_ip},
            },
            "bind": {
                "DNS_LISTEN_ON": enriched["DNS_LISTEN_ON"],
                "BIND_ADMIN_LISTEN_ON": enriched["BIND_ADMIN_LISTEN_ON"],
            },
            "distinct_bind_ips": distinct_ips,
            "admin_bind_ips": admin_ips,
            "audit": enriched["BIND_INTERFACE_AUDIT"],
        }

    def render_text(self) -> str:
        payload = self.as_dict()
        interfaces = payload["interfaces"]
        bind = payload["bind"]
        if not isinstance(interfaces, dict) or not isinstance(bind, dict):
            raise TypeError("invalid interface diagnostic payload")
        lines = [
            "DNSForge BIND interface diagnostics",
            f"setup_file={payload['setup_file']}",
        ]
        for role in ("extranet", "intranet", "admin"):
            item = interfaces[role]
            if not isinstance(item, dict):
                raise TypeError("invalid interface diagnostic item")
            lines.append(f"{role}.nic={item['nic']}")
            lines.append(f"{role}.ip={item['ip']}")
        lines.append(f"DNS_LISTEN_ON={bind['DNS_LISTEN_ON']}")
        lines.append(f"BIND_ADMIN_LISTEN_ON={bind['BIND_ADMIN_LISTEN_ON']}")
        lines.append(f"audit={payload['audit']}")
        return "\n".join(lines)

    def render_json(self) -> str:
        return json.dumps(self.as_dict(), indent=2, sort_keys=True)
