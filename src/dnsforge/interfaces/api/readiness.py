from __future__ import annotations

from dnsforge.application.readiness import ReadinessService
from dnsforge.domain.readiness import ReadinessReport
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class ReadinessApi:
    def __init__(self, paths: ProjectPaths) -> None:
        self.service = ReadinessService(paths)

    def report(self) -> ReadinessReport:
        return self.service.run()

    def status(self) -> dict[str, object]:
        return self.report().as_dict()
