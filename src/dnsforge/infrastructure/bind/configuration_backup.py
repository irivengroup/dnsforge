from __future__ import annotations

import datetime as dt
import shutil
import tarfile
from dataclasses import dataclass
from pathlib import Path

from dnsforge.infrastructure.bind.layout import BindLayout, BindLayoutDetector


@dataclass(frozen=True)
class BindConfigurationBackupResult:
    archive: Path
    moved_paths: tuple[Path, ...]
    dry_run: bool = False

    def summary(self) -> str:
        mode = "dry-run" if self.dry_run else "created"
        moved = ", ".join(str(path) for path in self.moved_paths) or "none"
        return f"bind_config_backup={mode}; archive={self.archive}; moved={moved}"


class BindConfigurationBackup:
    """Filesystem-level backup for the BIND configuration currently managed by the OS.

    DNSForge initialize intentionally takes ownership of BIND configuration files.
    Existing files/directories are moved out of their live locations first, then
    compressed as a tar.gz archive. This gives deterministic deployment semantics:
    no stale include, no mixed configuration tree, and an atomic audit trail.
    """

    def __init__(self, backup_root: Path = Path("/var/backups/dnsforge/bind-config"), layout: BindLayout | None = None) -> None:
        self.backup_root = backup_root
        self.layout = layout or BindLayoutDetector().detect()

    def create(
        self,
        target_root: Path = Path("/"),
        dry_run: bool = False,
        include_paths: tuple[Path, ...] | None = None,
    ) -> BindConfigurationBackupResult:
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        root = target_root.resolve()
        backup_dir = root / self.backup_root.relative_to("/") / stamp
        payload_dir = backup_dir / "payload"
        archive = backup_dir.with_suffix(".tar.gz")
        paths = include_paths or tuple(path.relative_to("/") for path in self.layout.backup_paths)

        existing: list[Path] = []
        for relative in paths:
            candidate = root / relative
            if candidate.exists() or candidate.is_symlink():
                existing.append(candidate)

        if dry_run:
            return BindConfigurationBackupResult(archive=archive, moved_paths=tuple(existing), dry_run=True)

        backup_dir.mkdir(parents=True, exist_ok=True)
        payload_dir.mkdir(parents=True, exist_ok=True)

        moved: list[Path] = []
        for source in existing:
            relative = source.relative_to(root)
            destination = payload_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            moved.append(source)

        with tarfile.open(archive, "w:gz") as tar:
            tar.add(payload_dir, arcname=".")

        shutil.rmtree(backup_dir)
        return BindConfigurationBackupResult(archive=archive, moved_paths=tuple(moved), dry_run=False)
