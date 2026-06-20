from __future__ import annotations

from pathlib import Path

from dnsforge.application.doctor.doctor_service import DoctorService
from dnsforge.application.status.status_service import StatusService


def test_status_includes_network_diagnostics_without_lock_path(tmp_path: Path) -> None:
    setup_file = tmp_path / "setup.conf"
    setup_file.write_text(
        'ROLE="proxy"\n'
        'PROXY_TYPE="hybrid"\n'
        'BIND_EXTRANET_IP="203.0.113.10"\n'
        'BIND_INTRANET_IP="10.0.0.10"\n'
        'BIND_ADMIN_IP="192.0.2.10"\n',
        encoding="utf-8",
    )

    output = StatusService().show(setup_file)

    assert "Network Interfaces:" in output
    assert "Extranet:" in output
    assert "DNS Listen On:" in output
    assert ".initialized.conf.lock" not in output


def test_doctor_warns_when_all_bind_planes_resolve_to_single_ip(tmp_path: Path) -> None:
    setup_file = tmp_path / "setup.conf"
    setup_file.write_text(
        'ROLE="dns-authoritative"\n'
        'ENABLE_RRL="yes"\n'
        'ENABLE_DNSSEC="yes"\n'
        'ENABLE_RPZ="yes"\n'
        'SECURITY_PROFILE="enterprise"\n'
        'BIND_EXTRANET_IP="192.0.2.10"\n'
        'BIND_INTRANET_IP="192.0.2.10"\n'
        'BIND_ADMIN_IP="192.0.2.10"\n',
        encoding="utf-8",
    )

    output = DoctorService().diagnose(setup_file)

    assert "single-NIC topology" in output
