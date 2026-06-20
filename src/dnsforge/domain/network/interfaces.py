from __future__ import annotations

from dataclasses import dataclass
import ipaddress


@dataclass(frozen=True)
class BindInterfaceSelection:
    """Operator-facing interface selection from setup.conf.

    DNSForge intentionally stores NIC names, not addresses, in setup.conf. The
    local agent resolves them at render time so a node can use one, two or three
    interfaces without copying volatile IP addresses into configuration.
    """

    external_nic: str
    intranet_nic: str
    admin_nic: str


@dataclass(frozen=True)
class ResolvedBindInterfaces:
    external_ip: str
    intranet_ip: str
    admin_ip: str

    def distinct_ips(self) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in (self.external_ip, self.intranet_ip, self.admin_ip):
            address = str(ipaddress.ip_interface(value).ip)
            if address not in seen:
                seen.add(address)
                result.append(address)
        return result
