from __future__ import annotations

from collections.abc import Iterable

from dnsforge.application.readiness.checks.bind_installed import BindInstalledCheck
from dnsforge.application.readiness.checks.initialization import InitializationCheck
from dnsforge.application.readiness.checks.platform_support import PlatformSupportCheck
from dnsforge.application.readiness.checks.python_version import PythonVersionCheck
from dnsforge.application.readiness.checks.repositories import BackupRepositoryCheck, HistoryRepositoryCheck
from dnsforge.application.readiness.readiness_check import ReadinessCheck
from dnsforge.domain.readiness import ReadinessReport, ReadinessResult, ReadinessStatus
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class ReadinessService:
    def __init__(self, paths: ProjectPaths, checks: Iterable[ReadinessCheck] | None = None) -> None:
        self.paths = paths
        self.checks = list(checks) if checks is not None else self._default_checks()

    def run(self) -> ReadinessReport:
        results: list[ReadinessResult] = []
        for check in self.checks:
            try:
                results.append(check.run())
            except Exception as exc:  # defensive isolation: one failed check must not hide the report
                results.append(
                    ReadinessResult(
                        getattr(check, "name", check.__class__.__name__),
                        ReadinessStatus.FAILED,
                        f"readiness check failed: {exc}",
                        critical=getattr(check, "critical", True),
                    )
                )
        return ReadinessReport(results)

    def _default_checks(self) -> list[ReadinessCheck]:
        return [
            PlatformSupportCheck(),
            PythonVersionCheck(),
            BindInstalledCheck(),
            InitializationCheck(self.paths),
            BackupRepositoryCheck(self.paths),
            HistoryRepositoryCheck(self.paths),
        ]
