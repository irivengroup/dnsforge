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
        target_root = target_root.resolve()
        with tarfile.open(backup, "r:gz") as tar:
            self._safe_extract(tar, target_root)

    @staticmethod
    def _safe_extract(tar: tarfile.TarFile, target_root: Path) -> None:
        for member in tar.getmembers():
            destination = BackupService._validate_member(member, target_root)
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
                destination.chmod(member.mode & 0o777)
                continue
            if not member.isfile():
                raise ValueError(f"unsupported backup archive member: {member.name}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            source = tar.extractfile(member)
            if source is None:
                raise ValueError(f"unable to read backup archive member: {member.name}")
            with source, destination.open("wb") as target:
                target.write(source.read())
            destination.chmod(member.mode & 0o777)

    @staticmethod
    def _validate_member(member: tarfile.TarInfo, target_root: Path) -> Path:
        member_name = member.name
        member_path = Path(member_name)

        if member_path.is_absolute():
            raise ValueError(f"unsafe absolute path in backup archive: {member_name}")

        destination = (target_root / member_path).resolve()
        try:
            destination.relative_to(target_root)
        except ValueError as exc:
            raise ValueError(f"unsafe path traversal in backup archive: {member_name}") from exc

        if member.issym() or member.islnk():
            raise ValueError(f"unsafe link member in backup archive: {member_name}")

        if member.isdev():
            raise ValueError(f"unsafe device member in backup archive: {member_name}")

        return destination
