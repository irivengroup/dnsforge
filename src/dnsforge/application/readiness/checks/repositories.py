from __future__ import annotations

from dnsforge.domain.readiness import ReadinessResult, ReadinessStatus
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class BackupRepositoryCheck:
    name = "Backup Repository"
    critical = True

    def __init__(self, paths: ProjectPaths) -> None:
        self.paths = paths

    def run(self) -> ReadinessResult:
        root = self.paths.backup_root
        if root.exists() and not root.is_dir():
            return ReadinessResult(self.name, ReadinessStatus.FAILED, "backup path exists but is not a directory", True)
        parent = root if root.exists() else root.parent
        if parent.exists():
            return ReadinessResult(self.name, ReadinessStatus.PASS, "backup repository parent is available", True)
        return ReadinessResult(self.name, ReadinessStatus.FAILED, "backup repository parent is missing", True)


class HistoryRepositoryCheck:
    name = "History Repository"
    critical = True

    def __init__(self, paths: ProjectPaths) -> None:
        self.paths = paths

    def run(self) -> ReadinessResult:
        root = self.paths.history_root
        if root.exists() and not root.is_dir():
            return ReadinessResult(
                self.name, ReadinessStatus.FAILED, "history path exists but is not a directory", True
            )
        parent = root if root.exists() else root.parent
        if parent.exists():
            return ReadinessResult(self.name, ReadinessStatus.PASS, "history repository parent is available", True)
        return ReadinessResult(self.name, ReadinessStatus.FAILED, "history repository parent is missing", True)
