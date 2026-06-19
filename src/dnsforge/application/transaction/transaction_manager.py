from __future__ import annotations

import datetime as dt
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


@dataclass(frozen=True)
class TransactionSnapshot:
    transaction_id: str
    root: Path
    files_root: Path
    metadata_file: Path


class FilesystemTransactionManager:
    """Generic filesystem transaction for DNSForge critical operations.

    The manager uses plain copies instead of archive extraction. This keeps
    rollback deterministic and avoids tar/zip path traversal classes of bugs.
    """

    def __init__(self, backup_root: Path) -> None:
        self.backup_root = backup_root

    def run(
        self,
        *,
        operation: str,
        paths: Iterable[Path],
        execute: Callable[[TransactionSnapshot], None],
        validate: Callable[[TransactionSnapshot], None] | None = None,
        target_root: Path = Path("/"),
        metadata: dict[str, str] | None = None,
    ) -> TransactionSnapshot:
        snapshot = self.snapshot(operation=operation, paths=paths, target_root=target_root, metadata=metadata or {})
        try:
            execute(snapshot)
            if validate is not None:
                validate(snapshot)
            self.mark(snapshot, "committed")
            return snapshot
        except Exception:
            self.restore(snapshot, target_root=target_root)
            self.mark(snapshot, "rolled_back")
            raise

    def snapshot(
        self,
        *,
        operation: str,
        paths: Iterable[Path],
        target_root: Path = Path("/"),
        metadata: dict[str, str] | None = None,
    ) -> TransactionSnapshot:
        transaction_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M%S%f")
        root = self.backup_root / operation / transaction_id
        files_root = root / "files"
        root.mkdir(parents=True, exist_ok=False)
        files_root.mkdir(parents=True, exist_ok=True)
        copied: list[str] = []
        for source in dict.fromkeys(paths):
            effective = self._effective_path(source, target_root)
            if not effective.exists():
                continue
            destination = files_root / self._relative_name(source)
            self._copy_path(effective, destination)
            copied.append(str(source))
        metadata_file = root / "metadata.json"
        payload = {
            "id": transaction_id,
            "operation": operation,
            "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "target_root": str(target_root),
            "paths": copied,
            "status": "prepared",
            **(metadata or {}),
        }
        metadata_file.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return TransactionSnapshot(transaction_id, root, files_root, metadata_file)

    def restore(self, snapshot: TransactionSnapshot, target_root: Path = Path("/")) -> None:
        if not snapshot.files_root.exists():
            return
        for stored in sorted(snapshot.files_root.rglob("*"), key=lambda item: len(item.parts)):
            if stored.is_dir():
                continue
            destination = target_root / stored.relative_to(snapshot.files_root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(stored, destination)

    def mark(self, snapshot: TransactionSnapshot, status: str) -> None:
        payload = json.loads(snapshot.metadata_file.read_text(encoding="utf-8"))
        payload["status"] = status
        payload["updated_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        snapshot.metadata_file.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _effective_path(self, path: Path, target_root: Path) -> Path:
        if target_root == Path("/"):
            return path
        return target_root / self._relative_name(path)

    def _relative_name(self, path: Path) -> Path:
        return Path(*path.parts[1:]) if path.is_absolute() else path

    def _copy_path(self, source: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(source, destination, symlinks=True)
            return
        shutil.copy2(source, destination)
