from __future__ import annotations

from dnsforge.domain.profile.model import ConfigurationProfile
from dnsforge.infrastructure.network.interface_resolver import InterfaceAddressResolver


class SetupProfileGenerator:
    """Generate setup.conf dynamically from profile policy and host defaults."""

    def __init__(self, resolver: InterfaceAddressResolver | None = None) -> None:
        self.resolver = resolver or InterfaceAddressResolver()

    def generate(
        self,
        profile: ConfigurationProfile,
        node: str,
        proxy_type: str | None = None,
    ) -> str:
        admin_nic = self.resolver.default_admin_interface()
        lines: list[str] = [
            "# DNSForge managed setup.conf",
            f"# Profile: {profile.value}",
            "# Network bindings are declared with NIC names. DNSForge resolves IPv4 addresses at render time.",
            "",
            "# ------------------------------------------------------------------------------",
            "# Identity",
            "# ------------------------------------------------------------------------------",
            f'ROLE="{profile.role}"',
            f'NODE_NAME="{node}"',
        ]
        if profile is not ConfigurationProfile.AUTHORITATIVE:
            lines.append(f'PROXY_TYPE="{proxy_type or profile.proxy_type or "hybrid"}"')
        lines.extend(
            [
                "",
                "# ------------------------------------------------------------------------------",
                "# Network",
                "# ------------------------------------------------------------------------------",
            ]
        )
        if profile is ConfigurationProfile.AUTHORITATIVE:
            lines.extend(
                [
                    f'BIND_INTRANET_NICNAME="{admin_nic}"',
                    f'BIND_ADMIN_NICNAME="{admin_nic}"',
                    'VIP_BACK_IP="REPLACE_VIP_BACK_IP"',
                    'PEER_BACK_IP="REPLACE_PEER_BACK_IP"',
                    'PEER_PROXY_ADDRESSES="REPLACE_PROXY_BACK_IP_1; REPLACE_PROXY_BACK_IP_2"',
                ]
            )
        else:
            lines.extend(
                [
                    f'BIND_EXTERNET_NICNAME="{admin_nic}"',
                    f'BIND_INTRANET_NICNAME="{admin_nic}"',
                    f'BIND_ADMIN_NICNAME="{admin_nic}"',
                    (
                        'PEER_AUTHORITATIVE_ADDRESSES="'
                        'REPLACE_AUTH_CLUSTER_VIP_OR_IP_1; REPLACE_AUTH_CLUSTER_VIP_OR_IP_2"'
                    ),
                    'PEER_PROXY_ADDRESSES=""',
                ]
            )
        lines.extend(self._common(profile))
        return "\n".join(lines).rstrip() + "\n"

    def _common(self, profile: ConfigurationProfile) -> list[str]:
        proxy = profile is not ConfigurationProfile.AUTHORITATIVE
        forwarder = profile is ConfigurationProfile.PROXY_FORWARDER
        hybrid = profile is ConfigurationProfile.PROXY_HYBRID
        return [
            "",
            "# ------------------------------------------------------------------------------",
            "# Features",
            "# ------------------------------------------------------------------------------",
            f'ENABLE_RPZ="{"yes" if proxy else "no"}"',
            'ENABLE_RRL="yes"',
            f'ENABLE_DNSSEC="{"no" if proxy else "yes"}"',
            f'ENABLE_PROXY_MASTER_ZONES="{"yes" if hybrid else "no"}"',
            f'ENABLE_PROXY_AUTHORITATIVE_ZONES="{"yes" if hybrid else "no"}"',
            f'ENABLE_PROXY_LOCAL_ZONES="{"yes" if hybrid else "no"}"',
            "",
            "# ------------------------------------------------------------------------------",
            "# Forwarding",
            "# ------------------------------------------------------------------------------",
            'DNS_FORWARDERS="1.1.1.1;8.8.8.8;"',
            'DNS_FORWARD_POLICY="first"',
            "",
            "# ------------------------------------------------------------------------------",
            "# RNDC / TSIG",
            "# ------------------------------------------------------------------------------",
            'RNDC_KEY_NAME="rndc-key"',
            'TSIG_KEY_NAME="xfr-shared-key"',
            'TSIG_SECRET="CHANGE_ME_BASE64"',
            "",
            "# ------------------------------------------------------------------------------",
            "# Security / ACL",
            "# ------------------------------------------------------------------------------",
            ('BACK_RECURSIVE_CLIENTS="10.0.0.0/8; 172.16.0.0/12; 192.168.0.0/16; localhost; localnets;"'),
            'ADM_ALLOWED_CLIENTS="REPLACE_ADM_CIDR"',
            'FRONT_ALLOWED_CLIENTS="any"',
            (
                'PROXY_TRANSFER_CLIENTS="none;"'
                if proxy
                else 'PROXY_TRANSFER_CLIENTS="REPLACE_PROXY_BACK_IP_1; REPLACE_PROXY_BACK_IP_2;"'
            ),
            "",
            "# ------------------------------------------------------------------------------",
            "# Additional settings",
            "# ------------------------------------------------------------------------------",
            'RPZ_ZONE_NAME="rpz.local"',
            'RPZ_POLICY="recursive-only yes"',
            'RPZ_LOGGING="yes"',
            'RRL_RESPONSES_PER_SECOND="10"',
            'RRL_REFERRALS_PER_SECOND="5"',
            'RRL_NXDOMAINS_PER_SECOND="5"',
            'RRL_ERRORS_PER_SECOND="5"',
            'RRL_WINDOW="5"',
            'DNSSEC_POLICY_NAME="binddns-default"',
            'DNSSEC_KEY_DIRECTORY="/var/named/dnssec"',
            'DNSSEC_SIGNING_MODE="policy"',
            'BINDDNS_VERSION="5.0"',
            'ZONE_ACL_PUBLIC="any;"',
            'ZONE_ACL_INTERNAL="recursive_clients;"',
            'ZONE_ACL_PARTNER="partner_clients;"',
            'PARTNER_ALLOWED_CLIENTS="203.0.113.0/24; localhost;"',
            'SECURITY_PROFILE="enterprise"',
            'ENABLE_DNS_COOKIES="yes"',
            'ENABLE_QNAME_MINIMIZATION="yes"',
            'ENABLE_SERVE_STALE="yes"',
            'HIDE_BIND_VERSION="yes"',
            'MINIMAL_RESPONSES="yes"',
            'MINIMAL_ANY="yes"',
            f'ENABLE_CLUSTER="{"no" if proxy else "yes"}"',
        ]
