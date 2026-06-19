from __future__ import annotations

import json

import pytest

from dnsforge_manager.domain.audit.models import ManagerAuditEvent
from dnsforge_manager.domain.inventory.models import ManagedNode, NodeRole, NodeStatus
from dnsforge_manager.domain.persistence import ManagerPersistenceConfig, PersistenceBackend
from dnsforge_manager.domain.workflows.models import ChangeRequestStatus, ManagerChangeRequest
from dnsforge_manager.infrastructure.persistence import PostgreSQLPersistenceBackend
from dnsforge_manager.infrastructure.persistence.postgresql import (
    PostgreSQLChangeRequestRepository,
    PostgreSQLManagerAuditRepository,
    PostgreSQLNodeInventoryRepository,
    PostgreSQLSchemaMigrator,
)
from dnsforge_manager.infrastructure.postgresql import MANAGER_SCHEMA_MIGRATIONS


class FakeCursor:
    def __init__(self, database: dict[str, dict[str, str]], audit: list[str]) -> None:
        self.database = database
        self.audit = audit
        self.result = None

    def execute(self, statement: str, parameters: tuple[object, ...] = ()) -> None:
        if statement.startswith("CREATE"):
            self.result = None
            return
        if "manager_nodes" in statement:
            self._execute_keyed("nodes", parameters)
        elif "manager_change_requests" in statement:
            self._execute_keyed("changes", parameters)
        elif "manager_audit_events" in statement:
            if statement.startswith("INSERT"):
                self.audit.append(str(parameters[0]))
                self.result = None
            else:
                self.result = [(payload,) for payload in self.audit]

    def _execute_keyed(self, table: str, parameters: tuple[object, ...]) -> None:
        if parameters and len(parameters) == 2:
            self.database[table][str(parameters[0])] = str(parameters[1]).replace("::jsonb", "")
            self.result = None
            return
        if parameters and len(parameters) == 1:
            payload = self.database[table].get(str(parameters[0]))
            self.result = None if payload is None else (payload,)
            return
        self.result = [(payload,) for _, payload in sorted(self.database[table].items())]

    def fetchone(self):
        return self.result

    def fetchall(self):
        return self.result or []


class FakeConnection:
    def __init__(self) -> None:
        self.database = {"nodes": {}, "changes": {}}
        self.audit: list[str] = []
        self.commits = 0
        self.statements: list[str] = []

    def cursor(self) -> FakeCursor:
        return FakeCursor(self.database, self.audit)

    def commit(self) -> None:
        self.commits += 1


def test_postgresql_backend_is_opt_in_and_dsn_validated():
    assert ManagerPersistenceConfig().backend is PersistenceBackend.JSON

    with pytest.raises(ValueError, match="backend=postgresql"):
        PostgreSQLPersistenceBackend(ManagerPersistenceConfig())

    backend = PostgreSQLPersistenceBackend(
        ManagerPersistenceConfig(backend=PersistenceBackend.POSTGRESQL, dsn="postgresql://manager@db/dnsforge")
    )
    assert backend.is_ready() is True


def test_postgresql_schema_migrator_applies_versioned_migrations():
    connection = FakeConnection()
    applied = PostgreSQLSchemaMigrator(connection).apply()

    assert applied == tuple(migration.version for migration in MANAGER_SCHEMA_MIGRATIONS)
    assert "001" in applied and "003" in applied
    assert connection.commits == 1


def test_postgresql_inventory_repository_round_trips_nodes():
    repository = PostgreSQLNodeInventoryRepository(FakeConnection())
    node = ManagedNode(
        node_id="dns01",
        name="dns01",
        api_endpoint="https://dns01.example/api",
        role=NodeRole.AUTHORITATIVE,
        agent_token="secret",
    )

    repository.register(node)
    repository.set_status("dns01", NodeStatus.ACTIVE)

    assert repository.get("dns01").status is NodeStatus.ACTIVE
    assert repository.list()[0].agent_token == "secret"


def test_postgresql_inventory_repository_rejects_duplicate_register():
    repository = PostgreSQLNodeInventoryRepository(FakeConnection())
    node = ManagedNode("dns01", "dns01", "https://dns01.example/api", NodeRole.AUTHORITATIVE)

    repository.register(node)

    with pytest.raises(ValueError, match="already registered"):
        repository.register(node)


def test_postgresql_change_repository_updates_status():
    repository = PostgreSQLChangeRequestRepository(FakeConnection())
    change = ManagerChangeRequest(
        change_id="chg-1",
        cluster_id="cluster-a",
        operation="zone.create",
        payload={"zone": "example.test"},
    )

    repository.save(change)
    repository.update_status("chg-1", ChangeRequestStatus.APPROVED, approved_by="admin")

    assert repository.get("chg-1").status is ChangeRequestStatus.APPROVED
    assert repository.list()[0].approved_by == "admin"


def test_postgresql_change_repository_rejects_unknown_status_field():
    repository = PostgreSQLChangeRequestRepository(FakeConnection())
    repository.save(
        ManagerChangeRequest(
            change_id="chg-1",
            cluster_id="cluster-a",
            operation="zone.create",
            payload={},
        )
    )

    with pytest.raises(ValueError, match="unsupported"):
        repository.update_status("chg-1", ChangeRequestStatus.FAILED, invalid=True)


def test_postgresql_audit_repository_appends_events():
    repository = PostgreSQLManagerAuditRepository(FakeConnection())
    event = ManagerAuditEvent(actor="admin", action="node.register", target="dns01", result="success")

    repository.append(event)

    assert repository.list()[0].to_dict()["action"] == "node.register"
    assert json.dumps(repository.list()[0].to_dict(), sort_keys=True)
