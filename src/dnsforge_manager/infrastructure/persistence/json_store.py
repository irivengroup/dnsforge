from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import TypeVar

T = TypeVar("T")


class JsonDocumentStore:
    """Atomic JSON document store shared by Manager repositories."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def read_items(self, key: str, factory: Callable[[dict[str, object]], T]) -> dict[str, T]:
        if not self.path.exists():
            return {}
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(f"{self.path} must contain a JSON object")
        values = raw.get(key, [])
        if not isinstance(values, list):
            raise ValueError(f"{self.path} key '{key}' must contain a list")
        items: dict[str, T] = {}
        for value in values:
            if not isinstance(value, dict):
                raise ValueError(f"{self.path} key '{key}' entries must be JSON objects")
            item = factory(value)
            item_id = str(getattr(item, "node_id", getattr(item, "change_id", "")))
            if not item_id:
                raise ValueError(f"{self.path} item in '{key}' has no stable identifier")
            items[item_id] = item
        return items

    def write_items(self, key: str, items: Iterable[dict[str, object]]) -> None:
        payload = {key: list(items)}
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(self.path)
