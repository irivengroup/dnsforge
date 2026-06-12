from __future__ import annotations

from dataclasses import dataclass

from dnsforge.domain.model.proxy_type import ProxyType


@dataclass(frozen=True)
class ProxyRenderProfile:
    proxy_type: ProxyType
    include_local_zones: bool
    include_zone_routing: bool
    include_master_directory: bool

    @classmethod
    def from_proxy_type(cls, proxy_type: ProxyType) -> "ProxyRenderProfile":
        if proxy_type is ProxyType.FORWARDER:
            return cls(
                proxy_type=proxy_type,
                include_local_zones=False,
                include_zone_routing=False,
                include_master_directory=False,
            )

        return cls(
            proxy_type=proxy_type,
            include_local_zones=True,
            include_zone_routing=True,
            include_master_directory=True,
        )
