from __future__ import annotations

from dnsforge_manager.domain.agent_control.models import AgentApiCommand, AgentApiResult, AgentApiTarget
from dnsforge_manager.domain.inventory.models import ManagedNode, NodeStatus
from dnsforge_manager.infrastructure.agent_control.client import AgentApiClient, RecordingAgentApiClient
from dnsforge_manager.infrastructure.concurrency import ParallelExecutor


class AgentApiControlService:
    """Central Manager service for executing DNSForge Agent API operations.

    The service validates that targets are trusted/reachable, fans out safely with auto-sized workers and keeps the
    Manager independent from local BIND files.
    """

    def __init__(self, client: AgentApiClient | None = None, executor: ParallelExecutor | None = None) -> None:
        self.client = client or RecordingAgentApiClient()
        self.executor = executor or ParallelExecutor()

    def execute(self, node: ManagedNode, command: AgentApiCommand) -> AgentApiResult:
        self._assert_node_eligible(node)
        return self.client.execute(self._target_from_node(node), command)

    def execute_many(self, nodes: tuple[ManagedNode, ...], command: AgentApiCommand) -> tuple[AgentApiResult, ...]:
        eligible = tuple(node for node in nodes if self._is_node_eligible(node))
        if not eligible:
            raise ValueError("no eligible DNSForge agents matched the requested target scope")
        return self.executor.map_ordered(
            eligible, lambda node: self.client.execute(self._target_from_node(node), command)
        )

    @staticmethod
    def _target_from_node(node: ManagedNode) -> AgentApiTarget:
        return AgentApiTarget(
            node_id=node.node_id,
            api_endpoint=node.api_endpoint,
            fingerprint=node.node_id,
            site=node.site,
            cluster=node.cluster_id,
        )

    @staticmethod
    def _is_node_eligible(node: ManagedNode) -> bool:
        return node.status not in {NodeStatus.DISABLED, NodeStatus.UNREACHABLE} and node.trust_state == "approved"

    @classmethod
    def _assert_node_eligible(cls, node: ManagedNode) -> None:
        if not cls._is_node_eligible(node):
            raise PermissionError(f"DNSForge agent {node.node_id!r} is not approved or reachable")
