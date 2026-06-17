from __future__ import annotations

import re
from pathlib import Path


class ProfileTemplateLoader:
    _assignment = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$")

    def load(self, path: Path) -> dict[str, str]:
        values: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            match = self._assignment.match(line)
            if match:
                key, raw = match.groups()
                values[key] = raw.strip()
        return values
