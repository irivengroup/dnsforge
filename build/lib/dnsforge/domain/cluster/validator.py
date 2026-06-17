from __future__ import annotations

import ipaddress

from dnsforge.domain.cluster.model import ClusterConfig, ClusterRole
from dnsforge.shared.errors import SettingsError


class ClusterValidator:
    def validate(self, config: ClusterConfig) -> None:
        if not config.enabled:
            return
        if config.dns_role and config.dns_role != "dns-authoritative":
            raise SettingsError("cluster is supported only for authoritative DNS servers")
        if config.role is None:
            raise SettingsError("cluster enabled but CLUSTER_ROLE is missing")
        if config.role is not ClusterRole.AUTHORITATIVE:
            raise SettingsError("cluster is supported only for authoritative DNS servers")
        if not config.local_node:
            raise SettingsError("cluster enabled but NODE_NAME is missing")
        if not config.peers:
            raise SettingsError("authoritative cluster requires at least one peer node")
        if config.local_node in config.peers:
            raise SettingsError("CLUSTER_PEERS must not contain the local NODE_NAME")
        if len(set(config.peers)) != len(config.peers):
            raise SettingsError("CLUSTER_PEERS contains duplicate entries")
        if not config.vip:
            raise SettingsError("authoritative cluster requires CLUSTER_VIP")
        if not config.interface:
            raise SettingsError("authoritative cluster requires CLUSTER_INTERFACE")
        if not 1 <= config.priority <= 254:
            raise SettingsError("CLUSTER_PRIORITY must be between 1 and 254")
        if not 1 <= config.vrid <= 255:
            raise SettingsError("CLUSTER_VRID must be between 1 and 255")
        self._validate_address(config.vip, "CLUSTER_VIP")
        for peer in config.peers:
            self._validate_peer(peer)

    def _validate_peer(self, value: str) -> None:
        if not value.strip():
            raise SettingsError("CLUSTER_PEERS contains an empty peer")
        try:
            ipaddress.ip_address(value)
        except ValueError:
            # Node names are allowed because some deployments render HA by inventory name.
            return

    def _validate_address(self, value: str, name: str) -> None:
        try:
            ipaddress.ip_address(value)
        except ValueError as exc:
            raise SettingsError(f"{name} must be an IP address") from exc
