from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PersistenceBackend(str, Enum):
    JSON = "json"
    POSTGRESQL = "postgresql"


@dataclass(frozen=True)
class ManagerPersistenceConfig:
    """Manager persistence configuration.

    JSON remains the default embedded backend. PostgreSQL is intentionally a
    prepared backend contract until the Manager moves to a multi-user database
    deployment model.
    """

    backend: PersistenceBackend = PersistenceBackend.JSON
    data_dir: str = "/var/lib/dnsforge-manager"
    dsn: str | None = None
