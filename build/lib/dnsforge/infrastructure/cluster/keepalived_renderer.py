from __future__ import annotations

from dnsforge.domain.cluster.model import ClusterConfig


class KeepalivedRenderer:
    def render(self, config: ClusterConfig) -> str:
        auth_pass = config.auth_pass or "dnsforge"
        peers = "\n".join(f"        {peer}" for peer in config.peers)
        return f"""vrrp_instance DNSFORGE_AUTHORITATIVE {{
    state {config.keepalived_state}
    interface {config.interface}
    virtual_router_id {config.vrid}
    priority {config.priority}
    advert_int 1

    authentication {{
        auth_type PASS
        auth_pass {auth_pass}
    }}

    unicast_peer {{
{peers}
    }}

    virtual_ipaddress {{
        {config.vip}
    }}
}}
"""
