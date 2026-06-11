from __future__ import annotations
import datetime as dt
import tarfile
from pathlib import Path


class BackupService:
    def __init__(self, backup_root: Path = Path("/var/backups/dnsforge")) -> None:
        self.backup_root = backup_root

    def create(self, project_root: Path, setup_file: Path, dry_run: bool = False) -> Path:
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
        archive = self.backup_root / f"dnsforge-{stamp}.tar.gz"
        if dry_run:
            return archive
        self.backup_root.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive, "w:gz") as tar:
            if setup_file.exists():
                tar.add(setup_file, arcname="etc/dnsforge/setup.conf")
            catalog = project_root / "src/dnsforge/infrastructure/build/catalog/zones.yml"
            if catalog.exists():
                tar.add(catalog, arcname="catalog/zones.yml")
            render = project_root / "src/render"
            if render.exists():
                tar.add(render, arcname="render")
        return archive

    def list(self) -> list[Path]:
        if not self.backup_root.exists():
            return []
        return sorted(self.backup_root.glob("dnsforge-*.tar.gz"))

    def restore(self, backup: Path, target_root: Path, dry_run: bool = False) -> None:
        if not backup.exists():
            raise FileNotFoundError(backup)
        if dry_run:
            return
        with tarfile.open(backup, "r:gz") as tar:
            tar.extractall(target_root)
