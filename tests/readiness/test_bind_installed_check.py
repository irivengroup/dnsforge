from __future__ import annotations

from dnsforge.application.readiness.checks.bind_installed import BindInstalledCheck
from dnsforge.domain.readiness import ReadinessStatus


def test_bind_installed_check_reports_missing_binary(monkeypatch) -> None:
    monkeypatch.setattr("shutil.which", lambda binary: None)

    result = BindInstalledCheck().run()

    assert result.status is ReadinessStatus.FAILED
    assert "named" in result.message


def test_bind_installed_check_passes_when_binaries_exist(monkeypatch) -> None:
    monkeypatch.setattr("shutil.which", lambda binary: f"/usr/bin/{binary}")

    result = BindInstalledCheck().run()

    assert result.status is ReadinessStatus.PASS
