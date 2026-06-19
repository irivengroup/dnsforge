from __future__ import annotations

from typing import Generic, Protocol, TypeVar

T = TypeVar("T")


class ManagerRepository(Protocol[T]):
    """Common Manager repository port used by JSON and future PostgreSQL backends."""

    def save(self, item: T) -> T: ...

    def get(self, item_id: str) -> T: ...

    def list(self) -> tuple[T, ...]: ...
