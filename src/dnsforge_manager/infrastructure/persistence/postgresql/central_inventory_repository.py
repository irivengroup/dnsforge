from __future__ import annotations

import json
from typing import Callable, TypeVar

from dnsforge_manager.domain.inventory.models import Agent, AgentStatus, Cluster, Environment, Site
from dnsforge_manager.infrastructure.persistence.postgresql.connection import ConnectionLike
from dnsforge_manager.infrastructure.inventory.central_repository import CentralInventoryRepository

T = TypeVar("T")


class PostgreSQLCentralInventoryRepository(CentralInventoryRepository):
    """PostgreSQL adapter for v14.2.0 Central Inventory.

    It uses the requested table names while storing aggregate payloads as JSONB to preserve schema flexibility.
    """

    def __init__(self, connection: ConnectionLike) -> None:
        self.connection = connection

    def _create(self, table: str, key: str, identifier: str, payload: dict[str, object]) -> None:
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT 1 FROM {table} WHERE {key} = %s", (identifier,))
        if cursor.fetchone() is not None:
            raise ValueError(f"inventory object already exists: {identifier}")
        cursor.execute(
            f"INSERT INTO {table} ({key}, payload) VALUES (%s, %s::jsonb)",
            (identifier, json.dumps(payload, sort_keys=True)),
        )
        self.connection.commit()

    def _upsert(self, table: str, key: str, identifier: str, payload: dict[str, object]) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            f"INSERT INTO {table} ({key}, payload) VALUES (%s, %s::jsonb) "
            f"ON CONFLICT ({key}) DO UPDATE SET payload = EXCLUDED.payload",
            (identifier, json.dumps(payload, sort_keys=True)),
        )
        self.connection.commit()

    def _list(self, table: str, key: str, factory: Callable[[dict[str, object]], T]) -> tuple[T, ...]:
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT payload FROM {table} ORDER BY {key}")
        return tuple(factory(_payload(row)) for row in cursor.fetchall())

    def create_site(self, site: Site) -> Site:
        self._create("sites", "site_id", site.site_id, site.to_dict())
        return site

    def list_sites(self) -> tuple[Site, ...]:
        return self._list("sites", "site_id", Site.from_dict)

    def create_cluster(self, cluster: Cluster) -> Cluster:
        self._create("clusters", "cluster_id", cluster.cluster_id, cluster.to_dict())
        return cluster

    def list_clusters(self) -> tuple[Cluster, ...]:
        return self._list("clusters", "cluster_id", Cluster.from_dict)

    def register_agent(self, agent: Agent) -> Agent:
        self._create("agents", "fingerprint", agent.fingerprint, agent.to_dict())
        return agent

    def list_agents(self) -> tuple[Agent, ...]:
        return self._list("agents", "fingerprint", Agent.from_dict)

    def create_environment(self, environment: Environment) -> Environment:
        self._create("environments", "environment_id", environment.environment_id, environment.to_dict())
        return environment

    def list_environments(self) -> tuple[Environment, ...]:
        values = self._list("environments", "environment_id", Environment.from_dict)
        return values or (Environment(environment_id="production", name="production"),)

    def set_agent_status(self, status: AgentStatus) -> AgentStatus:
        self._upsert("agent_status", "fingerprint", status.fingerprint, status.to_dict())
        return status

    def list_agent_status(self) -> tuple[AgentStatus, ...]:
        return self._list("agent_status", "fingerprint", AgentStatus.from_dict)


def _payload(row: object) -> dict[str, object]:
    value = row[0] if isinstance(row, tuple) else row
    if isinstance(value, str):
        parsed = json.loads(value)
        if not isinstance(parsed, dict):
            raise ValueError("PostgreSQL payload must be a JSON object")
        return parsed
    if isinstance(value, dict):
        return value
    raise TypeError("unsupported PostgreSQL payload row")
