from __future__ import annotations

from pathlib import Path

import pytest

from dnsforge.application.security.dnssec.dnssec_service import DnssecService
from dnsforge.shared.errors import DnsForgeError


def setup_file(tmp_path: Path) -> Path:
    key_dir = tmp_path / "keys"
    path = tmp_path / "setup.conf"
    path.write_text(
        f"""ROLE="dns-authoritative"
NODE_NAME="ns01"
DNSSEC_ENABLED="yes"
DNSSEC_KEY_DIRECTORY="{key_dir}"
""",
        encoding="utf-8",
    )
    return path


def test_dnssec_zone_lifecycle_generates_key_metadata(tmp_path: Path) -> None:
    service = DnssecService()
    setup = setup_file(tmp_path)

    assert "DNSSEC enabled" in service.enable(setup, "example.com", "enable dnssec test")
    assert "State: enabled" in service.status(setup, "example.com")
    assert "DNSSEC signed" in service.sign(setup, "example.com", "sign zone test")
    assert "State: signed" in service.status(setup, "example.com")
    assert "DNSSEC validation OK" == service.validate(setup, "example.com")
    assert list((tmp_path / "keys" / "example.com").glob("*.metadata"))


def test_dnssec_rotation_and_expiry_check(tmp_path: Path) -> None:
    service = DnssecService()
    setup = setup_file(tmp_path)

    service.enable(setup, "example.com", "enable dnssec test")
    assert "KSK rotated" in service.rotate_ksk(setup, "example.com", "rotate ksk test")
    assert "ZSK rotated" in service.rotate_zsk(setup, "example.com", "rotate zsk test")
    assert "DNSSEC key expiry OK" == service.check_expiry(setup, warn_days=1)


def test_dnssec_mutating_actions_require_reason(tmp_path: Path) -> None:
    service = DnssecService()
    setup = setup_file(tmp_path)

    with pytest.raises(DnsForgeError):
        service.enable(setup, "example.com", "short")
