from __future__ import annotations
import ipaddress
from dnsforge.domain.cluster.model import ClusterConfig, ClusterRole
from dnsforge.shared.errors import SettingsError

class ClusterValidator:
    def validate(self, config: ClusterConfig) -> None:
        if not config.enabled:
            return
        if config.role is None:
            raise SettingsError("cluster enabled but CLUSTER_ROLE is missing")
        if not config.local_node:
            raise SettingsError("cluster enabled but NODE_NAME is missing")
        if not config.peers:
            raise SettingsError("cluster enabled but CLUSTER_PEERS is empty")
        if config.role is ClusterRole.PROXY:
            if not config.vip:
                raise SettingsError("proxy cluster requires CLUSTER_VIP")
            if not config.interface:
                raise SettingsError("proxy cluster requires CLUSTER_INTERFACE")
            ipaddress.ip_address(config.vip)
        if config.role is ClusterRole.AUTHORITATIVE and config.vip:
            raise SettingsError("authoritative cluster must not use CLUSTER_VIP")
