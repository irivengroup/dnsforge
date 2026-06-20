from __future__ import annotations

from dnsforge_manager.domain.persistence.models import ManagerPersistenceConfig, PersistenceBackend


class PostgreSQLPersistenceBackend:
    """PostgreSQL backend readiness boundary."""

    def __init__(self, config: ManagerPersistenceConfig) -> None:
        if config.backend != PersistenceBackend.POSTGRESQL:
            raise ValueError("PostgreSQL backend requires backend=postgresql")
        if not config.dsn:
            raise ValueError("PostgreSQL backend requires a DSN")
        self.config = config

    def is_ready(self) -> bool:
        dsn = self.config.dsn
        return dsn is not None and dsn.startswith("postgresql://")
