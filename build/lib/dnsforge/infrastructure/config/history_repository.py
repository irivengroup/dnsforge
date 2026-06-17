from __future__ import annotations

import datetime as dt
import difflib
import hashlib
from pathlib import Path

from dnsforge import __version__
from dnsforge.domain.config.model import ConfigSnapshot
from dnsforge.shared.errors import SettingsError


class ConfigHistoryRepository:
    def __init__(self, root: Path) -> None:
        self.root = root

    def create_snapshot(self, content: str, reason: str) -> ConfigSnapshot:
        if not reason.strip():
            raise SettingsError("configuration history reason is required")
        self.root.mkdir(parents=True, exist_ok=True)
        identifier = self.next_identifier()
        timestamp = dt.datetime.now(dt.timezone.utc)
        checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
        path = self.root / f"{identifier:06d}.conf"
        body = "\n".join(f"  {line}" for line in content.splitlines())
        path.write_text(
            f"id: {identifier}\n"
            f"timestamp: {timestamp.isoformat()}\n"
            f"reason: {reason}\n"
            f"checksum: {checksum}\n"
            f"dnsforge_version: {__version__}\n"
            f"content: |\n"
            f"{body}\n",
            encoding="utf-8",
        )
        return ConfigSnapshot(identifier, timestamp, reason, checksum, __version__, content, path)

    def list(self) -> list[ConfigSnapshot]:
        if not self.root.exists():
            return []
        return [self._load(path) for path in sorted(self.root.glob("*.conf"))]

    def get(self, identifier: int) -> ConfigSnapshot:
        path = self.root / f"{identifier:06d}.conf"
        if not path.exists():
            raise SettingsError(f"configuration history id not found: {identifier}")
        return self._load(path)

    def latest(self) -> ConfigSnapshot | None:
        snapshots = self.list()
        return None if not snapshots else snapshots[-1]

    def next_identifier(self) -> int:
        snapshots = self.list()
        return 1 if not snapshots else max(item.identifier for item in snapshots) + 1

    def diff_current(self, current_content: str, identifier: int | None = None) -> str:
        snapshot = self.get(identifier) if identifier is not None else self.latest()
        if snapshot is None:
            return "No configuration snapshot available"
        return "".join(
            difflib.unified_diff(
                snapshot.content.splitlines(keepends=True),
                current_content.splitlines(keepends=True),
                fromfile=f"setup.conf@{snapshot.identifier}",
                tofile="setup.conf@current",
            )
        )

    def diff(self, id1: int, id2: int) -> str:
        left = self.get(id1)
        right = self.get(id2)
        return "".join(
            difflib.unified_diff(
                left.content.splitlines(keepends=True),
                right.content.splitlines(keepends=True),
                fromfile=f"setup.conf@{id1}",
                tofile=f"setup.conf@{id2}",
            )
        )

    def _load(self, path: Path) -> ConfigSnapshot:
        identifier = 0
        timestamp = dt.datetime.fromtimestamp(0, tz=dt.timezone.utc)
        reason = ""
        checksum = ""
        version = ""
        content_lines: list[str] = []
        in_content = False
        for line in path.read_text(encoding="utf-8").splitlines():
            if in_content:
                content_lines.append(line[2:] if line.startswith("  ") else line)
                continue
            if line.startswith("id:"):
                identifier = int(line.split(":", 1)[1].strip())
            elif line.startswith("timestamp:"):
                timestamp = dt.datetime.fromisoformat(line.split(":", 1)[1].strip())
            elif line.startswith("reason:"):
                reason = line.split(":", 1)[1].strip()
            elif line.startswith("checksum:"):
                checksum = line.split(":", 1)[1].strip()
            elif line.startswith("dnsforge_version:"):
                version = line.split(":", 1)[1].strip()
            elif line.startswith("content:"):
                in_content = True
        content = "\n".join(content_lines).rstrip() + "\n"
        return ConfigSnapshot(identifier, timestamp, reason, checksum, version, content, path)
