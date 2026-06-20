from __future__ import annotations

import json
from pathlib import Path

from dnsforge.application.network import InterfaceDiagnosticsService


class FakeResolver:
    def resolution_report(self, _settings):
        class Report:
            external_nic = "eth2"
            intranet_nic = "eth1"
            admin_nic = "eth0"
            external_ip = "203.0.113.10"
            intranet_ip = "10.0.0.10"
            admin_ip = "192.0.2.10"

        return Report()

    def enrich_settings(self, _settings):
        return {
            "DNS_LISTEN_ON": "203.0.113.10; 10.0.0.10; 192.0.2.10;",
            "BIND_ADMIN_LISTEN_ON": "127.0.0.1; 192.0.2.10;",
            "BIND_INTERFACE_AUDIT": "extranet:eth2->203.0.113.10, intranet:eth1->10.0.0.10, admin:eth0->192.0.2.10",
        }


def test_interface_diagnostics_service_renders_text_and_json(tmp_path: Path) -> None:
    setup = tmp_path / "setup.conf"
    setup.write_text('ROLE="proxy"\nBIND_EXTRANET_NICNAME="eth2"\n', encoding="utf-8")
    service = InterfaceDiagnosticsService(setup, resolver=FakeResolver())  # type: ignore[arg-type]

    text = service.render_text()
    payload = json.loads(service.render_json())

    assert "extranet.nic=eth2" in text
    assert "DNS_LISTEN_ON=203.0.113.10; 10.0.0.10; 192.0.2.10;" in text
    assert payload["interfaces"]["admin"]["ip"] == "192.0.2.10"
    assert payload["distinct_bind_ips"] == ["203.0.113.10", "10.0.0.10", "192.0.2.10"]


def test_interface_diagnostics_service_exports_stable_payload(tmp_path: Path) -> None:
    setup = tmp_path / "setup.conf"
    setup.write_text('ROLE="proxy"\nBIND_EXTRANET_NICNAME="eth2"\n', encoding="utf-8")
    output = tmp_path / "artifacts" / "network.json"
    service = InterfaceDiagnosticsService(setup, resolver=FakeResolver())  # type: ignore[arg-type]

    exported = service.export(output, "json")
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert exported == output
    assert payload["schema"] == "dnsforge.bind-interface-diagnostics.v1"
    assert payload["interfaces"]["extranet"]["nic"] == "eth2"


def test_interface_diagnostics_service_rejects_unknown_export_format(tmp_path: Path) -> None:
    setup = tmp_path / "setup.conf"
    setup.write_text('ROLE="proxy"\nBIND_EXTRANET_NICNAME="eth2"\n', encoding="utf-8")
    service = InterfaceDiagnosticsService(setup, resolver=FakeResolver())  # type: ignore[arg-type]

    try:
        service.render("yaml")  # type: ignore[arg-type]
    except ValueError as exc:
        assert "unsupported network diagnostic export format" in str(exc)
    else:
        raise AssertionError("unknown export format should be rejected")
