from __future__ import annotations

from dnsforge.application.readiness.checks.platform_support import PlatformSupportCheck
from dnsforge.domain.readiness import ReadinessStatus


def test_platform_support_accepts_ubuntu_22(tmp_path) -> None:
    os_release = tmp_path / "os-release"
    os_release.write_text('ID="ubuntu"\nVERSION_ID="22.04"\n', encoding="utf-8")

    result = PlatformSupportCheck(os_release).run()

    assert result.status is ReadinessStatus.PASS


def test_platform_support_rejects_debian_below_minimum(tmp_path) -> None:
    os_release = tmp_path / "os-release"
    os_release.write_text('ID="debian"\nVERSION_ID="9"\n', encoding="utf-8")

    result = PlatformSupportCheck(os_release).run()

    assert result.status is ReadinessStatus.FAILED
    assert result.critical is True
