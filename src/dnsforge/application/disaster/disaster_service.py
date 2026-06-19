from __future__ import annotations

import json
from pathlib import Path

from dnsforge.application.transaction.transaction_manager import FilesystemTransactionManager
from dnsforge.infrastructure.bind.layout import BindLayout, BindLayoutDetector
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class DisasterRecoveryService:
    def __init__(self, paths: ProjectPaths, layout: BindLayout | None = None) -> None:
        self.paths = paths
        self.layout = layout or BindLayoutDetector().detect()
        self.transactions = FilesystemTransactionManager(paths.backup_root / "disaster")

    def snapshot(self, reason: str, target_root: Path = Path("/")) -> str:
        clean = self._require_reason(reason)
        paths = [self.paths.setup_file, self.paths.catalog_file, *self.layout.backup_paths]
        snapshot = self.transactions.snapshot(
            operation="snapshot",
            paths=paths,
            target_root=target_root,
            metadata={"reason": clean, "scope": "setup,bind,zones,dnssec,catalog,cluster"},
        )
        self.transactions.mark(snapshot, "committed")
        return f"Disaster snapshot created: {snapshot.root}"

    def restore(self, snapshot: Path, target_root: Path = Path("/"), dry_run: bool = False) -> str:
        metadata_file = snapshot / "metadata.json"
        files_root = snapshot / "files"
        if not metadata_file.exists() or not files_root.exists():
            raise ValueError("invalid disaster snapshot")
        if dry_run:
            return f"Disaster restore dry-run OK: {snapshot}"
        from dnsforge.application.transaction.transaction_manager import TransactionSnapshot

        metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
        self.transactions.restore(
            TransactionSnapshot(metadata.get("id", snapshot.name), snapshot, files_root, metadata_file), target_root
        )
        return f"Disaster restore completed: {snapshot}"

    def verify(self, snapshot: Path) -> str:
        if not (snapshot / "metadata.json").exists():
            raise ValueError("missing metadata.json")
        if not (snapshot / "files").exists():
            raise ValueError("missing files directory")
        return "Disaster snapshot verification OK"

    def _require_reason(self, reason: str) -> str:
        clean = (reason or "").strip()
        if len(clean) < 8:
            raise ValueError("--reason is required and must contain at least 8 characters")
        return clean
