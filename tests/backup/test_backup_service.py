from __future__ import annotations

import io
import tarfile
from pathlib import Path

import pytest

from dnsforge.infrastructure.backup.backup_service import BackupService


def _write_tar(path: Path, member_name: str, content: bytes = b"payload") -> None:
    with tarfile.open(path, "w:gz") as tar:
        info = tarfile.TarInfo(member_name)
        info.size = len(content)
        tar.addfile(info, io.BytesIO(content))


def test_backup_restore_rejects_path_traversal(tmp_path: Path) -> None:
    archive = tmp_path / "unsafe.tar.gz"
    _write_tar(archive, "../../etc/passwd")

    with pytest.raises(ValueError, match="unsafe path traversal"):
        BackupService().restore(archive, tmp_path / "target")


def test_backup_restore_rejects_absolute_path(tmp_path: Path) -> None:
    archive = tmp_path / "unsafe-absolute.tar.gz"
    _write_tar(archive, "/etc/passwd")

    with pytest.raises(ValueError, match="unsafe absolute path"):
        BackupService().restore(archive, tmp_path / "target")


def test_backup_restore_accepts_safe_relative_member(tmp_path: Path) -> None:
    archive = tmp_path / "safe.tar.gz"
    _write_tar(archive, "etc/dnsforge/setup.conf", b"ROLE=dns-proxy\n")
    target = tmp_path / "target"

    BackupService().restore(archive, target)

    assert (target / "etc/dnsforge/setup.conf").read_text(encoding="utf-8") == "ROLE=dns-proxy\n"
