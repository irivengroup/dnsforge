from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class ChangeRequestLock:
    """Best-effort filesystem lock for JSON-backed change request mutations.

    The lock is deliberately local and dependency-free. PostgreSQL deployments
    will use row/advisory locks behind the same repository boundary.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def acquire(self) -> Iterator[None]:
        if self.path.exists():
            raise RuntimeError(f"change request repository is locked: {self.path}")
        self.path.write_text("locked\n", encoding="utf-8")
        try:
            yield
        finally:
            self.path.unlink(missing_ok=True)
