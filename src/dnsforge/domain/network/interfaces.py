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


@dataclass(frozen=True)
class BindInterfaceResolutionReport:
    """Auditable summary of DNSForge NIC to IPv4 resolution.

    The report is intentionally serializable as stable text so it can be
    surfaced in validation output, logs or support bundles without exposing
    runtime-only implementation details.
    """

    external_nic: str
    intranet_nic: str
    admin_nic: str
    external_ip: str
    intranet_ip: str
    admin_ip: str

    def as_settings(self) -> dict[str, str]:
        return {
            "BIND_EXTRANET_RESOLVED_FROM": self.external_nic,
            "BIND_INTRANET_RESOLVED_FROM": self.intranet_nic,
            "BIND_ADMIN_RESOLVED_FROM": self.admin_nic,
            "BIND_INTERFACE_AUDIT": self.render(),
        }

    def render(self) -> str:
        rows = (
            ("extranet", self.external_nic, self.external_ip),
            ("intranet", self.intranet_nic, self.intranet_ip),
            ("admin", self.admin_nic, self.admin_ip),
        )
        return ", ".join(f"{role}:{nic}->{ip}" for role, nic, ip in rows)
