from __future__ import annotations

from dnsforge.domain.readiness import ReadinessReport, ReadinessResult, ReadinessStatus
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.interfaces.api.readiness import ReadinessApi


def test_readiness_api_returns_stable_status(monkeypatch, tmp_path) -> None:
    report = ReadinessReport([ReadinessResult("Platform Support", ReadinessStatus.PASS, "ok", True)])
    monkeypatch.setattr("dnsforge.interfaces.api.readiness.ReadinessService.run", lambda self: report)

    status = ReadinessApi(ProjectPaths(tmp_path)).status()

    assert status["overall_status"] == "READY"
    assert status["score"] == 100
