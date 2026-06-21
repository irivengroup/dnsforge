#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> int:
    errors: list[str] = []
    required = [
        ROOT / "docs" / "MANAGER_POSTGRESQL_PERSISTENCE.md",
        ROOT / "src" / "dnsforge_manager" / "infrastructure" / "persistence" / "postgresql" / "inventory_repository.py",
        ROOT / "src" / "dnsforge_manager" / "infrastructure" / "persistence" / "postgresql" / "audit_repository.py",
        ROOT / "src" / "dnsforge_manager" / "infrastructure" / "persistence" / "postgresql" / "migrator.py",
    ]
    for path in required:
        if not path.exists():
            errors.append(f"missing PostgreSQL persistence artifact: {path.relative_to(ROOT)}")

    from dnsforge_manager.domain.persistence import ManagerPersistenceConfig, PersistenceBackend
    from dnsforge_manager.infrastructure.persistence import PostgreSQLPersistenceBackend
    from dnsforge_manager.infrastructure.postgresql import MANAGER_SCHEMA_MIGRATIONS

    if ManagerPersistenceConfig().backend is not PersistenceBackend.JSON:
        errors.append("JSON must remain the default Manager persistence backend")
    if len(MANAGER_SCHEMA_MIGRATIONS) < 3:
        errors.append("expected at least 3 Manager PostgreSQL schema migrations")
    backend = PostgreSQLPersistenceBackend(
        ManagerPersistenceConfig(backend=PersistenceBackend.POSTGRESQL, dsn="postgresql://manager@db/dnsforge")
    )
    if not backend.is_ready():
        errors.append("valid PostgreSQL DSN should mark backend readiness true")

    if errors:
        print("Manager PostgreSQL persistence gate failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Manager PostgreSQL persistence gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
