from __future__ import annotations

import re
from pathlib import Path

from dnsforge.shared.errors import SettingsError


class EnvSettingsLoader:
    _assignment = re.compile(r"""^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)\s*$""")

    def load(self, path: Path) -> dict[str, str]:
        if not path.exists():
            raise SettingsError(f"settings file not found: {path}")

        data: dict[str, str] = {}

        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            match = self._assignment.match(line)
            if not match:
                continue

            key, raw = match.groups()
            raw = raw.strip()

            if raw and raw[0] not in {"'", '"'}:
                raw = raw.split("#", 1)[0].strip()

            data[key] = self._strip_quotes(raw)

        return data

    def _strip_quotes(self, value: str) -> str:
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            return value[1:-1]
        return value
