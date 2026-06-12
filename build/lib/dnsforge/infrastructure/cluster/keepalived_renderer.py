from __future__ import annotations

from dnsforge.domain.cluster.model import ClusterConfig


class KeepalivedRenderer:
    def render(self, config: ClusterConfig) -> str:
        auth_pass = config.auth_pass or "dnsforge"
        state = "MASTER" if config.priority >= 150 else "BACKUP"
        return f"""vrrp_instance DNSFORGE_DNS {{
    state {state}
    interface {config.interface}
    virtual_router_id 53
    priority {config.priority}
    advert_int 1

    authentication {{
        auth_type PASS
        auth_pass {auth_pass}
    }}

    virtual_ipaddress {{
        {config.vip}
    }}
}}
"""
