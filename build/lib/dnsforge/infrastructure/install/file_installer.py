from __future__ import annotations

import datetime as dt
import shutil
from pathlib import Path


class FileInstaller:
    def backup_root(self, target_root: Path = Path("/")) -> Path:
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M%S")
        return target_root / "var/backups/dnsforge" / stamp

    def install_tree(
        self, render_root: Path, target_root: Path = Path("/"), dry_run: bool = True
    ) -> list[tuple[Path, Path]]:
        mappings: list[tuple[Path, Path]] = []

        if not render_root.exists():
            raise FileNotFoundError(f"render root not found: {render_root}")

        for source in render_root.rglob("*"):
            if source.is_dir():
                continue

            relative = source.relative_to(render_root)
            destination = target_root / relative
            mappings.append((source, destination))

            if not dry_run:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)

        return mappings
