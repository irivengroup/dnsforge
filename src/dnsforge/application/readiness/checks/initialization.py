from __future__ import annotations

from pathlib import Path

from dnsforge.domain.readiness import ReadinessResult, ReadinessStatus
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class InitializationCheck:
    name = "Initialization"
    critical = True

    def __init__(self, paths: ProjectPaths) -> None:
        self.paths = paths

    def run(self) -> ReadinessResult:
        setup_exists = self.paths.setup_file.exists()
        lock_file = self.paths.settings_root / ".initialized.conf.lock"
        if setup_exists and lock_file.exists():
            return ReadinessResult(self.name, ReadinessStatus.PASS, "DNSForge node is initialized", True)
        if setup_exists:
            return ReadinessResult(
                self.name,
                ReadinessStatus.WARNING,
                "setup.conf exists but initialization lock is not present",
                False,
            )
        return ReadinessResult(
            self.name,
            ReadinessStatus.FAILED,
            "DNSForge node is not initialized",
            critical=self.critical,
        )
