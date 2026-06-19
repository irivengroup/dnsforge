from __future__ import annotations

import hashlib
from pathlib import Path

from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class DriftService:
    """Detect local drift between rendered DNSForge state and native BIND target files."""

    def __init__(self, paths: ProjectPaths) -> None:
        self.paths = paths

    def audit(self, *, target_root: Path = Path("/")) -> tuple[bool, str]:
        render_root = self.paths.render_root
        if not render_root.exists():
            return (
                False,
                "ERROR: no rendered configuration found; run dnsforge render or initialize --render-only first",
            )
        findings: list[str] = []
        for source in sorted(path for path in render_root.rglob("*") if path.is_file()):
            relative = source.relative_to(render_root)
            target = target_root / relative
            if not target.exists():
                findings.append(f"MISSING\t{relative}")
                continue
            if self._sha256(source) != self._sha256(target):
                findings.append(f"CHANGED\t{relative}")
        if findings:
            return False, "DNSForge drift detected\n" + "\n".join(findings)
        return True, "DNSForge drift audit OK"

    def _sha256(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
