from __future__ import annotations

import pytest

from dnsforge_manager.domain.inventory.models import ManagedNode, NodeRole
from dnsforge_manager.domain.persistence import ManagerPersistenceConfig, PersistenceBackend
from dnsforge_manager.infrastructure.inventory import JsonNodeInventoryRepository
from dnsforge_manager.infrastructure.persistence import PostgreSQLPersistenceBackend
from dnsforge_manager.infrastructure.postgresql import MANAGER_SCHEMA_MIGRATIONS


def test_json_inventory_repository_keeps_existing_default_backend(tmp_path):
    path = tmp_path / "nodes.json"
    repository = JsonNodeInventoryRepository(path)
    node = ManagedNode(
        node_id="dns01",
        name="dns01",
        api_endpoint="https://dns01.example/api",
        role=NodeRole.AUTHORITATIVE,
        agent_token="secret-token",
    )

    repository.register(node)
    reloaded = JsonNodeInventoryRepository(path)

    assert reloaded.get("dns01").agent_token == "secret-token"
    assert reloaded.list()[0].node_id == "dns01"


def test_postgresql_schema_tracks_dnssync_not_change_management():
    descriptions = {migration.version: migration.description for migration in MANAGER_SCHEMA_MIGRATIONS}
    statements = "\n".join(statement for migration in MANAGER_SCHEMA_MIGRATIONS for statement in migration.statements)

    assert descriptions["002"] == "manager dnssync orchestration"
    assert "dnssync_plans" in statements
    assert "manager_change_requests" not in statements


def test_postgresql_backend_is_prepared_but_not_default_runtime_dependency():
    assert ManagerPersistenceConfig().backend is PersistenceBackend.JSON
    assert MANAGER_SCHEMA_MIGRATIONS[0].version == "001"
    assert "manager_nodes" in MANAGER_SCHEMA_MIGRATIONS[0].statements[0]

    backend = PostgreSQLPersistenceBackend(
        ManagerPersistenceConfig(
            backend=PersistenceBackend.POSTGRESQL,
            dsn="postgresql://manager@db/dnsforge",
        )
    )
    assert backend.is_ready() is True

    with pytest.raises(ValueError, match="DSN"):
        PostgreSQLPersistenceBackend(ManagerPersistenceConfig(backend=PersistenceBackend.POSTGRESQL))
