from __future__ import annotations

import pytest

from dnsforge_manager.application.persistence import ChangeRequestLock
from dnsforge_manager.application.workflows import (
    JsonChangeRequestRepository,
    ManagerChangeWorkflow,
)
from dnsforge_manager.domain.inventory.models import ManagedNode, NodeRole
from dnsforge_manager.domain.persistence import ManagerPersistenceConfig, PersistenceBackend
from dnsforge_manager.domain.workflows.models import ChangeRequestStatus, ManagerChangeRequest
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


def test_json_change_request_repository_persists_and_locks(tmp_path):
    path = tmp_path / "changes.json"
    repository = JsonChangeRequestRepository(path)
    change = ManagerChangeRequest(
        change_id="chg-1",
        cluster_id="cluster-a",
        operation="zone.create",
        payload={"zone": "example.test"},
    )

    repository.save(change)
    repository.update_status("chg-1", ChangeRequestStatus.APPROVED, approved_by="admin")
    reloaded = JsonChangeRequestRepository(path).get("chg-1")

    assert reloaded.status is ChangeRequestStatus.APPROVED
    assert reloaded.approved_by == "admin"


def test_change_request_lock_rejects_concurrent_mutation(tmp_path):
    lock = ChangeRequestLock(tmp_path / "changes.lock")

    with lock.acquire():
        with pytest.raises(RuntimeError, match="locked"):
            with lock.acquire():
                pass

    assert not (tmp_path / "changes.lock").exists()


def test_manager_workflow_accepts_json_change_repository(tmp_path):
    workflow = ManagerChangeWorkflow(repository=JsonChangeRequestRepository(tmp_path / "changes.json"))
    change = workflow.create_change(
        ManagerChangeRequest(
            cluster_id="cluster-a",
            operation="zone.create",
            payload={"zone": "example.test"},
        )
    )

    persisted_change = JsonChangeRequestRepository(tmp_path / "changes.json").get(change.change_id)
    assert persisted_change.status is ChangeRequestStatus.PENDING


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
    assert backend.is_ready() is False

    with pytest.raises(ValueError, match="DSN"):
        PostgreSQLPersistenceBackend(ManagerPersistenceConfig(backend=PersistenceBackend.POSTGRESQL))
