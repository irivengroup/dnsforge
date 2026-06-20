from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from dnsforge_manager.domain.inventory.models import (
    Agent,
    AgentComplianceEvent,
    AgentComplianceStatus,
    AgentReadiness,
    AgentStatus,
    Cluster,
    ConfigurationComplianceState,
    Environment,
    Site,
)
from dnsforge_manager.infrastructure.inventory.central_repository import (
    CentralInventoryRepository,
    InMemoryCentralInventoryRepository,
)


class CentralInventoryService:
    def __init__(self, repository: CentralInventoryRepository | None = None) -> None:
        self.repository = repository or InMemoryCentralInventoryRepository()

    def create_site(self, payload: dict[str, object]) -> Site:
        return self.repository.create_site(
            Site(
                site_id=str(payload["site_id"]),
                name=str(payload.get("name", payload["site_id"])),
                description=str(payload.get("description", "")),
                labels=_labels(payload.get("labels", {})),
            )
        )

    def list_sites(self) -> tuple[Site, ...]:
        return self.repository.list_sites()

    def create_cluster(self, payload: dict[str, object]) -> Cluster:
        return self.repository.create_cluster(
            Cluster(
                cluster_id=str(payload["cluster_id"]),
                name=str(payload.get("name", payload["cluster_id"])),
                site=str(payload.get("site", "default")),
                environment=str(payload.get("environment", "production")),
                description=str(payload.get("description", "")),
                labels=_labels(payload.get("labels", {})),
            )
        )

    def list_clusters(self) -> tuple[Cluster, ...]:
        return self.repository.list_clusters()

    def register_agent(self, payload: dict[str, object]) -> Agent:
        agent = Agent(
            fingerprint=str(payload["fingerprint"]),
            hostname=str(payload["hostname"]),
            version=str(payload["version"]),
            profile=str(payload["profile"]),
            site=str(payload.get("site", "default")),
            cluster=None if payload.get("cluster") is None else str(payload.get("cluster")),
            status=AgentReadiness(str(payload.get("status", AgentReadiness.WARNING.value))),
            labels=_labels(payload.get("labels", {})),
        )
        registered = self.repository.register_agent(agent)
        self.repository.set_agent_status(
            AgentStatus(
                fingerprint=registered.fingerprint,
                readiness=registered.status,
                hostname=registered.hostname,
                version=registered.version,
                profile=registered.profile,
                site=registered.site,
                cluster=registered.cluster,
                message="agent registered",
            )
        )
        return registered

    def list_agents(self) -> tuple[Agent, ...]:
        return self.repository.list_agents()

    def list_environments(self) -> tuple[Environment, ...]:
        return self.repository.list_environments()

    def update_agent_status(self, payload: dict[str, object]) -> AgentStatus:
        return self.repository.set_agent_status(AgentStatus.from_dict(payload))

    def list_agent_status(self) -> tuple[AgentStatus, ...]:
        return self.repository.list_agent_status()

    def aggregate_readiness(self) -> dict[str, object]:
        statuses = self.repository.list_agent_status()
        order = {AgentReadiness.READY: 0, AgentReadiness.WARNING: 1, AgentReadiness.FAILED: 2}
        aggregate = max(
            (status.readiness for status in statuses),
            key=lambda value: order[value],
            default=AgentReadiness.READY,
        )
        return {
            "status": aggregate.value,
            "agents": [status.to_dict() for status in statuses],
            "summary": {
                state.value: sum(1 for item in statuses if item.readiness == state) for state in AgentReadiness
            },
        }

    def update_agent_compliance(self, payload: dict[str, object]) -> AgentComplianceStatus:
        status = AgentComplianceStatus.from_dict(payload)
        previous = next(
            (item for item in self.repository.list_agent_compliance() if item.fingerprint == status.fingerprint),
            None,
        )
        stored = self.repository.set_agent_compliance(status)
        self.repository.append_agent_compliance_event(
            AgentComplianceEvent(
                event_id=str(uuid4()),
                fingerprint=stored.fingerprint,
                compliance=stored.compliance,
                drift_count=stored.drift_count,
                observed_at=stored.last_checked or datetime.now(timezone.utc).isoformat(),
                previous_compliance=None if previous is None else previous.compliance,
                previous_drift_count=None if previous is None else previous.drift_count,
                message=stored.message,
                transition=(
                    previous is None
                    or previous.compliance != stored.compliance
                    or previous.drift_count != stored.drift_count
                ),
            )
        )
        return stored

    def list_agent_compliance(self) -> tuple[AgentComplianceStatus, ...]:
        return self.repository.list_agent_compliance()

    def list_agent_compliance_history(self, fingerprint: str | None = None) -> tuple[AgentComplianceEvent, ...]:
        return self.repository.list_agent_compliance_events(fingerprint)

    def aggregate_compliance(self) -> dict[str, object]:
        statuses = self.repository.list_agent_compliance()
        order = {
            ConfigurationComplianceState.COMPLIANT: 0,
            ConfigurationComplianceState.WARNING: 1,
            ConfigurationComplianceState.DRIFTED: 2,
            ConfigurationComplianceState.FAILED: 3,
        }
        aggregate = max(
            (status.compliance for status in statuses),
            key=lambda value: order[value],
            default=ConfigurationComplianceState.COMPLIANT,
        )
        return {
            "status": aggregate.value,
            "agents": [status.to_dict() for status in statuses],
            "summary": {
                state.value: sum(1 for item in statuses if item.compliance == state)
                for state in ConfigurationComplianceState
            },
            "drift_count": sum(item.drift_count for item in statuses),
            "history_count": len(self.repository.list_agent_compliance_events()),
        }


def _labels(value: object) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("labels must be a mapping")
    return {str(key): str(item) for key, item in value.items()}
