from __future__ import annotations

from dnsforge.infrastructure.network.interface_resolver import InterfaceAddressResolver


class _Resolver(InterfaceAddressResolver):
    def default_admin_interface(self) -> str:
        return "eth0"

    def ipv4_for_interface(self, nic_name: str) -> str:
        return {"eth0": "10.0.0.10", "eth1": "10.0.1.10", "eth2": "203.0.113.10"}[nic_name]


def test_interface_resolver_defaults_all_bind_nics_to_admin_interface() -> None:
    enriched = _Resolver().enrich_settings({})

    assert enriched["BIND_EXTRANET_IP"] == "10.0.0.10"
    assert enriched["BIND_INTRANET_IP"] == "10.0.0.10"
    assert enriched["BIND_ADMIN_IP"] == "10.0.0.10"
    assert enriched["BIND_EXTRANET_IP"] == "10.0.0.10"
    assert enriched["BIND_INTRANET_IP"] == "10.0.0.10"
    assert enriched["BIND_ADMIN_IP"] == "10.0.0.10"
    assert enriched["DNS_LISTEN_ON"] == "10.0.0.10;"


def test_interface_resolver_filters_duplicate_bind_addresses() -> None:
    enriched = _Resolver().enrich_settings(
        {
            "BIND_EXTRANET_NICNAME": "eth2",
            "BIND_INTRANET_NICNAME": "eth1",
            "BIND_ADMIN_NICNAME": "eth1",
        }
    )

    assert enriched["BIND_EXTRANET_IP"] == "203.0.113.10"
    assert enriched["BIND_INTRANET_IP"] == "10.0.1.10"
    assert enriched["BIND_ADMIN_IP"] == "10.0.1.10"
    assert enriched["BIND_EXTRANET_IP"] == "203.0.113.10"
    assert enriched["BIND_INTRANET_IP"] == "10.0.1.10"
    assert enriched["BIND_ADMIN_IP"] == "10.0.1.10"
    assert enriched["DNS_LISTEN_ON"] == "203.0.113.10; 10.0.1.10;"
    assert enriched["BIND_ADMIN_LISTEN_ON"] == "127.0.0.1; 10.0.1.10;"


def test_interface_resolver_preserves_runtime_ip_values_for_migration() -> None:
    enriched = _Resolver().enrich_settings(
        {
            "BIND_EXTRANET_IP": "192.0.2.10",
            "BIND_INTRANET_IP": "192.0.2.11",
            "BIND_ADMIN_IP": "192.0.2.12",
        }
    )

    assert enriched["BIND_EXTRANET_IP"] == "192.0.2.10"
    assert enriched["BIND_INTRANET_IP"] == "192.0.2.11"
    assert enriched["BIND_ADMIN_IP"] == "192.0.2.12"
    assert enriched["BIND_EXTRANET_IP"] == "192.0.2.10"
    assert enriched["BIND_INTRANET_IP"] == "192.0.2.11"
    assert enriched["BIND_ADMIN_IP"] == "192.0.2.12"
    assert enriched["DNS_LISTEN_ON"] == "192.0.2.10; 192.0.2.11; 192.0.2.12;"


def test_interface_resolver_accepts_runtime_ip_values_for_migration() -> None:
    enriched = _Resolver().enrich_settings(
        {
            "BIND_EXTRANET_IP": "198.51.100.10",
            "BIND_INTRANET_IP": "198.51.100.11",
            "BIND_ADMIN_IP": "198.51.100.12",
        }
    )

    assert enriched["BIND_EXTRANET_IP"] == "198.51.100.10"
    assert enriched["BIND_INTRANET_IP"] == "198.51.100.11"
    assert enriched["BIND_ADMIN_IP"] == "198.51.100.12"
    assert enriched["BIND_EXTRANET_IP"] == "198.51.100.10"
    assert enriched["BIND_INTRANET_IP"] == "198.51.100.11"
    assert enriched["BIND_ADMIN_IP"] == "198.51.100.12"


def test_interface_resolver_ignores_removed_externet_alias() -> None:
    enriched = _Resolver().enrich_settings({"BIND_EXTERNET_NICNAME": "eth2"})

    assert enriched["BIND_EXTRANET_IP"] == "10.0.0.10"
    assert enriched["DNS_LISTEN_ON"] == "10.0.0.10;"


def test_interface_resolver_admin_listen_on_filters_loopback_duplicates() -> None:
    class LoopbackResolver(_Resolver):
        def default_admin_interface(self) -> str:
            return "lo"

        def ipv4_for_interface(self, nic_name: str) -> str:
            if nic_name == "lo":
                return "127.0.0.1"
            return super().ipv4_for_interface(nic_name)

    enriched = LoopbackResolver().enrich_settings({})

    assert enriched["BIND_ADMIN_LISTEN_ON"] == "127.0.0.1;"


def test_interface_resolver_exposes_auditable_resolution_report() -> None:
    resolver = _Resolver()
    settings = {
        "BIND_EXTRANET_NICNAME": "eth2",
        "BIND_INTRANET_NICNAME": "eth1",
        "BIND_ADMIN_NICNAME": "eth0",
    }

    enriched = resolver.enrich_settings(settings)
    report = resolver.resolution_report(settings)

    assert enriched["BIND_EXTRANET_RESOLVED_FROM"] == "eth2"
    assert enriched["BIND_INTRANET_RESOLVED_FROM"] == "eth1"
    assert enriched["BIND_ADMIN_RESOLVED_FROM"] == "eth0"
    assert enriched["BIND_INTERFACE_AUDIT"] == (
        "extranet:eth2->203.0.113.10, intranet:eth1->10.0.1.10, admin:eth0->10.0.0.10"
    )
    assert report.render() == enriched["BIND_INTERFACE_AUDIT"]
