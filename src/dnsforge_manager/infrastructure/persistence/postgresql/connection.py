from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class CursorLike(Protocol):
    def execute(self, statement: str, parameters: tuple[object, ...] = ()) -> Any: ...
    def fetchone(self) -> Any: ...
    def fetchall(self) -> Any: ...


class ConnectionLike(Protocol):
    def cursor(self) -> CursorLike: ...
    def commit(self) -> None: ...


@dataclass(frozen=True)
class PostgreSQLConnectionConfig:
    host: str
    database: str
    user: str
    password: str | None = None
    port: int = 5432

    @classmethod
    def from_dsn(cls, dsn: str) -> PostgreSQLConnectionConfig:
        if not dsn.startswith("postgresql://"):
            raise ValueError("PostgreSQL DSN must start with postgresql://")
        return cls(host="dsn", database=dsn, user="dsn")
