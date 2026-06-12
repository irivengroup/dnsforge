from __future__ import annotations

import ipaddress
from dataclasses import dataclass


@dataclass(frozen=True)
class ReverseMapping:
    """Reverse DNS mapping generated from a forward A/AAAA record.

    DNSForge manages reverse zones as first-class DNS zones. For IPv4, the
    default generated scope is /24 because it is the operationally common
    delegation boundary in Enterprise BIND deployments. IPv6 defaults to a
    host-exact reverse zone until DNSForge exposes delegated IPv6 prefix
    management.
    """

    zone_name: str
    ptr_owner: str
    ptr_target: str


def reverse_mapping_for_address(address: str, target_fqdn: str) -> ReverseMapping:
    ip = ipaddress.ip_address(address)
    target = target_fqdn if target_fqdn.endswith(".") else f"{target_fqdn}."
    if isinstance(ip, ipaddress.IPv4Address):
        octets = str(ip).split(".")
        zone_name = ".".join(reversed(octets[:3])) + ".in-addr.arpa"
        return ReverseMapping(zone_name=zone_name, ptr_owner=octets[3], ptr_target=target)

    nibbles = ip.exploded.replace(":", "")
    reversed_nibbles = ".".join(reversed(nibbles))
    return ReverseMapping(zone_name=f"{reversed_nibbles}.ip6.arpa", ptr_owner="@", ptr_target=target)


def is_reverse_zone_name(name: str) -> bool:
    lowered = name.rstrip(".").lower()
    return lowered.endswith(".in-addr.arpa") or lowered.endswith(".ip6.arpa")
