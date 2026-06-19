from __future__ import annotations

from dnsforge_manager.infrastructure.persistence.postgresql.connection import ConnectionLike
from dnsforge_manager.infrastructure.postgresql import MANAGER_SCHEMA_MIGRATIONS


class PostgreSQLSchemaMigrator:
    """Applies idempotent Manager PostgreSQL schema migrations."""

    def __init__(self, connection: ConnectionLike) -> None:
        self.connection = connection

    def apply(self) -> tuple[str, ...]:
        applied: list[str] = []
        cursor = self.connection.cursor()
        for migration in MANAGER_SCHEMA_MIGRATIONS:
            for statement in migration.statements:
                cursor.execute(statement)
            applied.append(migration.version)
        self.connection.commit()
        return tuple(applied)
