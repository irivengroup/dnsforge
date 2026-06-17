from __future__ import annotations

import re


class ListParser:
    def normalize(self, raw: str | None) -> list[str]:
        if not raw:
            return []
        return [item for item in re.split(r"[\s,;]+", raw.strip()) if item]
