from __future__ import annotations

from dnsforge.application.readiness import ReadinessService
from dnsforge.domain.readiness import ReadinessResult, ReadinessStatus
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class StaticCheck:
    name = "Static"
    critical = True

    def __init__(self, status: ReadinessStatus) -> None:
        self.status = status

    def run(self) -> ReadinessResult:
        return ReadinessResult(self.name, self.status, self.status.value, critical=self.critical)


def test_readiness_report_is_ready_when_all_checks_pass(tmp_path) -> None:
    report = ReadinessService(ProjectPaths(tmp_path), checks=[StaticCheck(ReadinessStatus.PASS)]).run()

    assert report.overall_label == "READY"
    assert report.score == 100
    assert "OVERALL STATUS : READY" in report.render()


def test_readiness_report_fails_on_critical_failure(tmp_path) -> None:
    report = ReadinessService(ProjectPaths(tmp_path), checks=[StaticCheck(ReadinessStatus.FAILED)]).run()

    assert report.overall_label == "FAILED"
    assert report.score == 0
