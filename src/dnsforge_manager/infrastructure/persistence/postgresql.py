from __future__ import annotations

from dnsforge_manager.domain.persistence.models import ManagerPersistenceConfig, PersistenceBackend


class PostgreSQLPersistenceBackend:
    """Prepared PostgreSQL backend boundary.

    The v12.6.1 release keeps JSON as the operational default and exposes a
    typed PostgreSQL readiness object so future migrations can implement the
    adapter without changing application services.
    """

    def __init__(self, config: ManagerPersistenceConfig) -> None:
        if config.backend != PersistenceBackend.POSTGRESQL:
            raise ValueError("PostgreSQL backend requires backend=postgresql")
        if not config.dsn:
            raise ValueError("PostgreSQL backend requires a DSN")
        self.config = config

    def is_ready(self) -> bool:
        return False
