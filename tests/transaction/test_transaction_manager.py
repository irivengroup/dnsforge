from __future__ import annotations

from pathlib import Path

import pytest

from dnsforge.application.transaction.transaction_manager import FilesystemTransactionManager


def test_transaction_manager_restores_files_on_failure(tmp_path: Path) -> None:
    target = tmp_path / "target"
    file_path = target / "etc" / "named.conf"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("before", encoding="utf-8")
    manager = FilesystemTransactionManager(tmp_path / "backups")

    def execute(_snapshot):
        file_path.write_text("after", encoding="utf-8")
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        manager.run(operation="unit", paths=[Path("/etc/named.conf")], target_root=target, execute=execute)

    assert file_path.read_text(encoding="utf-8") == "before"


def test_transaction_manager_marks_commit(tmp_path: Path) -> None:
    target = tmp_path / "target"
    file_path = target / "etc" / "named.conf"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("before", encoding="utf-8")
    manager = FilesystemTransactionManager(tmp_path / "backups")

    snapshot = manager.run(
        operation="unit",
        paths=[Path("/etc/named.conf")],
        target_root=target,
        execute=lambda _snapshot: file_path.write_text("after", encoding="utf-8"),
    )

    assert '"status": "committed"' in snapshot.metadata_file.read_text(encoding="utf-8")
    assert file_path.read_text(encoding="utf-8") == "after"
