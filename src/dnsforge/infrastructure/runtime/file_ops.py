from __future__ import annotations

from pathlib import Path
import shutil
import tempfile


class AtomicFileWriter:
    def write_text(self, path: Path, content: str, mode: int | None = None) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(path.parent), delete=False) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)
        if mode is not None:
            tmp_path.chmod(mode)
        shutil.move(str(tmp_path), str(path))


class BackupFile:
    def create(self, path: Path, suffix: str = ".bak") -> Path | None:
        if not path.exists():
            return None
        backup = path.with_name(path.name + suffix)
        shutil.copy2(path, backup)
        return backup
