from __future__ import annotations

from typing import Any, Protocol


class AsyncConnectionLike(Protocol):
    async def execute(self, statement: str, parameters: tuple[object, ...] = ()) -> Any:
        """Execute one PostgreSQL statement asynchronously."""
        ...

    async def fetch(self, statement: str, parameters: tuple[object, ...] = ()) -> list[Any]:
        """Fetch rows asynchronously using the driver-native cursor implementation."""
        ...
