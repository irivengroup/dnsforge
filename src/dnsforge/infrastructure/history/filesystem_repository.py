from __future__ import annotations

import datetime as dt
import difflib
from pathlib import Path

from dnsforge.domain.history.model import ZoneSnapshot
from dnsforge.shared.errors import ZoneError


class FilesystemHistoryRepository:
    def __init__(self, root: Path = Path("/var/lib/dnsforge/history")) -> None:
        self.root = root

    def zone_dir(self, zone: str) -> Path:
        return self.root / zone.replace("/", "_").replace("..", "_")

    def create_snapshot(self, zone: str, content: str, action: str) -> ZoneSnapshot:
        directory = self.zone_dir(zone)
        directory.mkdir(parents=True, exist_ok=True)

        version = self.next_version(zone)
        timestamp = dt.datetime.now(dt.timezone.utc)
        path = directory / f"{version:06d}.yml"

        body = "\n".join(f"  {line}" for line in content.splitlines())
        path.write_text(
            f"zone: {zone}\n"
            f"version: {version}\n"
            f"timestamp: {timestamp.isoformat()}\n"
            f"action: {action}\n"
            f"content: |\n"
            f"{body}\n",
            encoding="utf-8",
        )

        return ZoneSnapshot(zone, version, timestamp, action, content, path)

    def list(self, zone: str) -> list[ZoneSnapshot]:
        directory = self.zone_dir(zone)
        if not directory.exists():
            return []
        return [self._load(path) for path in sorted(directory.glob("*.yml"))]

    def get(self, zone: str, version: int) -> ZoneSnapshot:
        path = self.zone_dir(zone) / f"{version:06d}.yml"
        if not path.exists():
            raise ZoneError(f"history version not found: {zone}#{version}")
        return self._load(path)

    def next_version(self, zone: str) -> int:
        snapshots = self.list(zone)
        return 1 if not snapshots else max(snapshot.version for snapshot in snapshots) + 1

    def current_version(self, zone: str) -> int:
        snapshots = self.list(zone)
        return 0 if not snapshots else max(snapshot.version for snapshot in snapshots)

    def diff(self, zone: str, from_version: int, to_version: int) -> str:
        left = self.get(zone, from_version)
        right = self.get(zone, to_version)
        return "".join(
            difflib.unified_diff(
                left.content.splitlines(keepends=True),
                right.content.splitlines(keepends=True),
                fromfile=f"{zone}@{from_version}",
                tofile=f"{zone}@{to_version}",
            )
        )

    def _load(self, path: Path) -> ZoneSnapshot:
        zone = ""
        version = 0
        timestamp = dt.datetime.fromtimestamp(0, tz=dt.timezone.utc)
        action = ""
        content_lines: list[str] = []
        in_content = False

        for line in path.read_text(encoding="utf-8").splitlines():
            if in_content:
                content_lines.append(line[2:] if line.startswith("  ") else line)
                continue

            if line.startswith("zone:"):
                zone = line.split(":", 1)[1].strip()
            elif line.startswith("version:"):
                version = int(line.split(":", 1)[1].strip())
            elif line.startswith("timestamp:"):
                timestamp = dt.datetime.fromisoformat(line.split(":", 1)[1].strip())
            elif line.startswith("action:"):
                action = line.split(":", 1)[1].strip()
            elif line.startswith("content:"):
                in_content = True

        return ZoneSnapshot(
            zone=zone,
            version=version,
            timestamp=timestamp,
            action=action,
            content="\n".join(content_lines).rstrip() + "\n",
            path=path,
        )
