from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Callable, Generic, TypeVar

from dnsforge_manager.domain.inventory.models import Agent, AgentReadiness, AgentStatus, Cluster, Environment, Site

T = TypeVar("T")


class CentralInventoryRepository:
    def create_site(self, site: Site) -> Site:
        raise NotImplementedError

    def list_sites(self) -> tuple[Site, ...]:
        raise NotImplementedError

    def create_cluster(self, cluster: Cluster) -> Cluster:
        raise NotImplementedError

    def list_clusters(self) -> tuple[Cluster, ...]:
        raise NotImplementedError

    def register_agent(self, agent: Agent) -> Agent:
        raise NotImplementedError

    def list_agents(self) -> tuple[Agent, ...]:
        raise NotImplementedError

    def list_environments(self) -> tuple[Environment, ...]:
        raise NotImplementedError

    def create_environment(self, environment: Environment) -> Environment:
        raise NotImplementedError

    def set_agent_status(self, status: AgentStatus) -> AgentStatus:
        raise NotImplementedError

    def list_agent_status(self) -> tuple[AgentStatus, ...]:
        raise NotImplementedError


class _MemoryTable(Generic[T]):
    def __init__(self, identifier: Callable[[T], str]) -> None:
        self.identifier = identifier
        self.items: dict[str, T] = {}

    def create(self, item: T) -> T:
        key = self.identifier(item)
        if key in self.items:
            raise ValueError(f"inventory object already exists: {key}")
        self.items[key] = item
        return item

    def upsert(self, item: T) -> T:
        self.items[self.identifier(item)] = item
        return item

    def list(self) -> tuple[T, ...]:
        return tuple(self.items[key] for key in sorted(self.items))


class InMemoryCentralInventoryRepository(CentralInventoryRepository):
    def __init__(self) -> None:
        self.sites = _MemoryTable(lambda item: item.site_id)
        self.clusters = _MemoryTable(lambda item: item.cluster_id)
        self.agents = _MemoryTable(lambda item: item.fingerprint)
        self.environments = _MemoryTable(lambda item: item.environment_id)
        self.status = _MemoryTable(lambda item: item.fingerprint)
        self.environments.create(Environment(environment_id="production", name="production"))

    def create_site(self, site: Site) -> Site:
        return self.sites.create(site)

    def list_sites(self) -> tuple[Site, ...]:
        return self.sites.list()

    def create_cluster(self, cluster: Cluster) -> Cluster:
        return self.clusters.create(cluster)

    def list_clusters(self) -> tuple[Cluster, ...]:
        return self.clusters.list()

    def register_agent(self, agent: Agent) -> Agent:
        return self.agents.create(agent)

    def list_agents(self) -> tuple[Agent, ...]:
        return self.agents.list()

    def create_environment(self, environment: Environment) -> Environment:
        return self.environments.create(environment)

    def list_environments(self) -> tuple[Environment, ...]:
        return self.environments.list()

    def set_agent_status(self, status: AgentStatus) -> AgentStatus:
        return self.status.upsert(status)

    def list_agent_status(self) -> tuple[AgentStatus, ...]:
        return self.status.list()


class JsonCentralInventoryRepository(CentralInventoryRepository):
    """Default Manager Central Inventory backend.

    The file is intentionally independent from the legacy nodes inventory file so v14.2.0 can evolve the Manager
    source-of-truth model without changing the local DNSForge agent contract.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> dict[str, list[dict[str, object]]]:
        if not self.path.exists():
            return {"sites": [], "clusters": [], "agents": [], "environments": [], "agent_status": []}
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(f"{self.path} must contain a JSON object")
        return {
            "sites": _list(raw.get("sites", [])),
            "clusters": _list(raw.get("clusters", [])),
            "agents": _list(raw.get("agents", [])),
            "environments": _list(raw.get("environments", [])),
            "agent_status": _list(raw.get("agent_status", [])),
        }

    def _write(self, data: dict[str, list[dict[str, object]]]) -> None:
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(self.path)

    def _create(self, key: str, identifier: str, payload: dict[str, object]) -> None:
        data = self._read()
        if any(str(item.get(identifier)) == str(payload[identifier]) for item in data[key]):
            raise ValueError(f"inventory object already exists: {payload[identifier]}")
        data[key].append(payload)
        data[key] = sorted(data[key], key=lambda item: str(item.get(identifier, "")))
        self._write(data)

    def _upsert(self, key: str, identifier: str, payload: dict[str, object]) -> None:
        data = self._read()
        value = str(payload[identifier])
        data[key] = [item for item in data[key] if str(item.get(identifier)) != value]
        data[key].append(payload)
        data[key] = sorted(data[key], key=lambda item: str(item.get(identifier, "")))
        self._write(data)

    def create_site(self, site: Site) -> Site:
        self._create("sites", "site_id", site.to_dict())
        return site

    def list_sites(self) -> tuple[Site, ...]:
        return tuple(Site.from_dict(item) for item in self._read()["sites"])

    def create_cluster(self, cluster: Cluster) -> Cluster:
        self._create("clusters", "cluster_id", cluster.to_dict())
        return cluster

    def list_clusters(self) -> tuple[Cluster, ...]:
        return tuple(Cluster.from_dict(item) for item in self._read()["clusters"])

    def register_agent(self, agent: Agent) -> Agent:
        self._create("agents", "fingerprint", agent.to_dict())
        return agent

    def list_agents(self) -> tuple[Agent, ...]:
        return tuple(Agent.from_dict(item) for item in self._read()["agents"])

    def create_environment(self, environment: Environment) -> Environment:
        self._create("environments", "environment_id", environment.to_dict())
        return environment

    def list_environments(self) -> tuple[Environment, ...]:
        environments = tuple(Environment.from_dict(item) for item in self._read()["environments"])
        if environments:
            return environments
        return (Environment(environment_id="production", name="production"),)

    def set_agent_status(self, status: AgentStatus) -> AgentStatus:
        self._upsert("agent_status", "fingerprint", status.to_dict())
        return status

    def list_agent_status(self) -> tuple[AgentStatus, ...]:
        return tuple(AgentStatus.from_dict(item) for item in self._read()["agent_status"])


def _list(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        raise ValueError("inventory collections must be lists")
    result: list[dict[str, object]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("inventory collection entries must be JSON objects")
        result.append(item)
    return result
