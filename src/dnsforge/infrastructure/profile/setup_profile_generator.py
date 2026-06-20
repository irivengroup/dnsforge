from __future__ import annotations

from collections.abc import Mapping

from dnsforge.domain.profile.model import ConfigurationProfile
from dnsforge.infrastructure.network.interface_resolver import InterfaceAddressResolver

SetupValue = str | bool | None
SetupSection = Mapping[str, SetupValue]
DEFAULT_SETUP_PLACEHOLDER = "CHANGE_ME_BASE64"


class SetupProfileGenerator:
    """Generate setup.conf dynamically from composable profile dictionaries.

    setup.conf is intentionally generated from layered dictionaries instead of
    hard-coded full-line templates. This keeps the profile policy extensible:

    * common_setup: applies to every DNSForge node.
    * proxy_common_setup: applies to every proxy node.
    * autoritative_setup: applies to authoritative nodes only.
    * hybrid_setup: applies to proxy-hybrid nodes only.
    * forwader_setup: applies to proxy-forwarder nodes only.

    The historical misspellings ``autoritative`` and ``forwader`` are kept for
    operator alignment with the v14.5.x design note; aliases with the correct
    spelling are also exposed for maintainers.
    """

    common_setup: dict[str, SetupValue] = {
        "ROLE": None,
        "NODE_NAME": None,
        "BIND_ADMIN_NICNAME": None,
        "ENABLE_RRL": "yes",
        "DNS_FORWARDERS": "1.1.1.1;8.8.8.8;",
        "DNS_FORWARD_POLICY": "first",
        "RNDC_KEY_NAME": "rndc-key",
        "TSIG_KEY_NAME": "xfr-shared-key",
        "TSIG_SECRET": DEFAULT_SETUP_PLACEHOLDER,
        "BACK_RECURSIVE_CLIENTS": "10.0.0.0/8; 172.16.0.0/12; 192.168.0.0/16; localhost; localnets;",
        "ADM_ALLOWED_CLIENTS": "REPLACE_ADM_CIDR",
        "FRONT_ALLOWED_CLIENTS": "any",
        "RPZ_ZONE_NAME": "rpz.local",
        "RPZ_POLICY": "recursive-only yes",
        "RPZ_LOGGING": "yes",
        "RRL_RESPONSES_PER_SECOND": "10",
        "RRL_REFERRALS_PER_SECOND": "5",
        "RRL_NXDOMAINS_PER_SECOND": "5",
        "RRL_ERRORS_PER_SECOND": "5",
        "RRL_WINDOW": "5",
        "DNSSEC_POLICY_NAME": "binddns-default",
        "DNSSEC_KEY_DIRECTORY": "/var/named/dnssec",
        "DNSSEC_SIGNING_MODE": "policy",
        "BINDDNS_VERSION": "5.0",
        "ZONE_ACL_PUBLIC": "any;",
        "ZONE_ACL_INTERNAL": "recursive_clients;",
        "ZONE_ACL_PARTNER": "partner_clients;",
        "PARTNER_ALLOWED_CLIENTS": "203.0.113.0/24; localhost;",
        "SECURITY_PROFILE": "enterprise",
        "ENABLE_DNS_COOKIES": "yes",
        "ENABLE_QNAME_MINIMIZATION": "yes",
        "ENABLE_SERVE_STALE": "yes",
        "HIDE_BIND_VERSION": "yes",
        "MINIMAL_RESPONSES": "yes",
        "MINIMAL_ANY": "yes",
    }

    proxy_common_setup: dict[str, SetupValue] = {
        "PROXY_TYPE": None,
        "BIND_EXTERNET_NICNAME": None,
        "BIND_INTRANET_NICNAME": None,
        "PEER_AUTHORITATIVE_ADDRESSES": "REPLACE_AUTH_CLUSTER_VIP_OR_IP_1; REPLACE_AUTH_CLUSTER_VIP_OR_IP_2",
        "PEER_PROXY_ADDRESSES": "",
        "ENABLE_RPZ": "yes",
        "ENABLE_DNSSEC": "no",
        "ENABLE_CLUSTER": "no",
        "PROXY_TRANSFER_CLIENTS": "none;",
    }

    autoritative_setup: dict[str, SetupValue] = {
        "BIND_INTRANET_NICNAME": None,
        "VIP_BACK_IP": "REPLACE_VIP_BACK_IP",
        "PEER_BACK_IP": "REPLACE_PEER_BACK_IP",
        "PEER_PROXY_ADDRESSES": "REPLACE_PROXY_BACK_IP_1; REPLACE_PROXY_BACK_IP_2",
        "ENABLE_RPZ": "no",
        "ENABLE_DNSSEC": "yes",
        "ENABLE_CLUSTER": "yes",
        "ENABLE_PROXY_MASTER_ZONES": "no",
        "ENABLE_PROXY_AUTHORITATIVE_ZONES": "no",
        "ENABLE_PROXY_LOCAL_ZONES": "no",
        "PROXY_TRANSFER_CLIENTS": "REPLACE_PROXY_BACK_IP_1; REPLACE_PROXY_BACK_IP_2;",
    }

    hybrid_setup: dict[str, SetupValue] = {
        "ENABLE_PROXY_MASTER_ZONES": "yes",
        "ENABLE_PROXY_AUTHORITATIVE_ZONES": "yes",
        "ENABLE_PROXY_LOCAL_ZONES": "yes",
    }

    forwader_setup: dict[str, SetupValue] = {
        "ENABLE_PROXY_MASTER_ZONES": "no",
        "ENABLE_PROXY_AUTHORITATIVE_ZONES": "no",
        "ENABLE_PROXY_LOCAL_ZONES": "no",
    }

    authoritative_setup = autoritative_setup
    forwarder_setup = forwader_setup

    _SECTIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("Identity", ("ROLE", "NODE_NAME", "PROXY_TYPE")),
        (
            "Network",
            (
                "BIND_EXTERNET_NICNAME",
                "BIND_INTRANET_NICNAME",
                "BIND_ADMIN_NICNAME",
                "VIP_BACK_IP",
                "PEER_BACK_IP",
                "PEER_AUTHORITATIVE_ADDRESSES",
                "PEER_PROXY_ADDRESSES",
            ),
        ),
        (
            "Features",
            (
                "ENABLE_RPZ",
                "ENABLE_RRL",
                "ENABLE_DNSSEC",
                "ENABLE_CLUSTER",
                "ENABLE_PROXY_MASTER_ZONES",
                "ENABLE_PROXY_AUTHORITATIVE_ZONES",
                "ENABLE_PROXY_LOCAL_ZONES",
            ),
        ),
        ("Forwarding", ("DNS_FORWARDERS", "DNS_FORWARD_POLICY")),
        ("RNDC / TSIG", ("RNDC_KEY_NAME", "TSIG_KEY_NAME", "TSIG_SECRET")),
        (
            "Security / ACL",
            (
                "BACK_RECURSIVE_CLIENTS",
                "ADM_ALLOWED_CLIENTS",
                "FRONT_ALLOWED_CLIENTS",
                "PROXY_TRANSFER_CLIENTS",
            ),
        ),
        (
            "Additional settings",
            (
                "RPZ_ZONE_NAME",
                "RPZ_POLICY",
                "RPZ_LOGGING",
                "RRL_RESPONSES_PER_SECOND",
                "RRL_REFERRALS_PER_SECOND",
                "RRL_NXDOMAINS_PER_SECOND",
                "RRL_ERRORS_PER_SECOND",
                "RRL_WINDOW",
                "DNSSEC_POLICY_NAME",
                "DNSSEC_KEY_DIRECTORY",
                "DNSSEC_SIGNING_MODE",
                "BINDDNS_VERSION",
                "ZONE_ACL_PUBLIC",
                "ZONE_ACL_INTERNAL",
                "ZONE_ACL_PARTNER",
                "PARTNER_ALLOWED_CLIENTS",
                "SECURITY_PROFILE",
                "ENABLE_DNS_COOKIES",
                "ENABLE_QNAME_MINIMIZATION",
                "ENABLE_SERVE_STALE",
                "HIDE_BIND_VERSION",
                "MINIMAL_RESPONSES",
                "MINIMAL_ANY",
            ),
        ),
    )

    def __init__(self, resolver: InterfaceAddressResolver | None = None) -> None:
        self.resolver = resolver or InterfaceAddressResolver()

    def generate(
        self,
        profile: ConfigurationProfile,
        node: str,
        proxy_type: str | None = None,
    ) -> str:
        values = self._profile_values(profile=profile, node=node, proxy_type=proxy_type)
        lines = [
            "# DNSForge managed setup.conf",
            f"# Profile: {profile.value}",
            "# Network bindings are declared with NIC names. DNSForge resolves IPv4 addresses at render time.",
        ]
        lines.extend(self._render_sections(values))
        return "\n".join(lines).rstrip() + "\n"

    def _profile_values(
        self,
        profile: ConfigurationProfile,
        node: str,
        proxy_type: str | None,
    ) -> dict[str, str]:
        admin_nic = self.resolver.default_admin_interface()
        values = dict(self.common_setup)
        values.update(
            {
                "ROLE": profile.role,
                "NODE_NAME": node,
                "BIND_ADMIN_NICNAME": admin_nic,
            }
        )

        if profile is ConfigurationProfile.AUTHORITATIVE:
            values.update(self.autoritative_setup)
            values["BIND_INTRANET_NICNAME"] = admin_nic
        else:
            effective_proxy_type = proxy_type or profile.proxy_type or "hybrid"
            values.update(self.proxy_common_setup)
            values.update(
                {
                    "PROXY_TYPE": effective_proxy_type,
                    "BIND_EXTERNET_NICNAME": admin_nic,
                    "BIND_INTRANET_NICNAME": admin_nic,
                }
            )
            if profile is ConfigurationProfile.PROXY_FORWARDER:
                values.update(self.forwader_setup)
            else:
                values.update(self.hybrid_setup)

        return {key: str(value) for key, value in values.items() if value is not None}

    def _render_sections(self, values: Mapping[str, str]) -> list[str]:
        rendered: list[str] = []
        emitted: set[str] = set()
        for title, keys in self._SECTIONS:
            section_lines = [self._render_assignment(key, values[key]) for key in keys if key in values]
            if not section_lines:
                continue
            rendered.extend(
                [
                    "",
                    "# ------------------------------------------------------------------------------",
                    f"# {title}",
                    "# ------------------------------------------------------------------------------",
                    *section_lines,
                ]
            )
            emitted.update(key for key in keys if key in values)

        remaining = [key for key in values if key not in emitted]
        if remaining:
            rendered.extend(
                [
                    "",
                    "# ------------------------------------------------------------------------------",
                    "# Extended settings",
                    "# ------------------------------------------------------------------------------",
                ]
            )
            rendered.extend(self._render_assignment(key, values[key]) for key in remaining)
        return rendered

    @staticmethod
    def _render_assignment(key: str, value: str) -> str:
        escaped = value.replace('"', '\\"')
        return f'{key}="{escaped}"'
