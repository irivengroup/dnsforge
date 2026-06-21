from __future__ import annotations

import json
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dnsforge_manager.domain.agent_control.models import AgentApiCommand, AgentApiResult, AgentApiTarget


class AgentApiClient(Protocol):
    def execute(self, target: AgentApiTarget, command: AgentApiCommand) -> AgentApiResult:
        """Execute one DNSForge Agent API command against a trusted target."""
        ...


class RecordingAgentApiClient:
    def __init__(self) -> None:
        self.calls: list[tuple[AgentApiTarget, AgentApiCommand]] = []

    def execute(self, target: AgentApiTarget, command: AgentApiCommand) -> AgentApiResult:
        self.calls.append((target, command))
        return AgentApiResult(
            node_id=target.node_id,
            action=command.action.value,
            operation=command.operation,
            accepted=True,
            status_code=202,
            message="recorded",
            request_id=command.request_id,
            response={"recorded": True, "idempotency_key": command.idempotency_key},
        )


class UrlLibAgentApiClient:
    """Dependency-free DNSForge Agent API client.

    The client uses explicit endpoints, no shell commands and request-scoped idempotency/audit headers.
    TLS validation is delegated to Python's default HTTPS context. A future mTLS-enabled adapter can implement the
    same AgentApiClient protocol without changing the Manager application layer.
    """

    def __init__(self, token: str | None = None) -> None:
        self.token = token

    def execute(self, target: AgentApiTarget, command: AgentApiCommand) -> AgentApiResult:
        body = json.dumps(
            {
                "action": command.action.value,
                "operation": command.operation,
                "payload": command.payload,
                "request_id": command.request_id,
                "idempotency_key": command.idempotency_key,
            }
        ).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "X-DNSForge-Request-ID": command.request_id,
            "X-DNSForge-Idempotency-Key": command.idempotency_key,
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        endpoint = target.api_endpoint.rstrip("/") + "/api/v1/commands"
        request = Request(endpoint, data=body, headers=headers, method="POST")
        try:
            with urlopen(request, timeout=command.timeout_seconds) as response:  # nosec B310
                payload = response.read().decode("utf-8")
                parsed = json.loads(payload or "{}")
                if not isinstance(parsed, dict):
                    parsed = {"raw": parsed}
                status_code = int(getattr(response, "status", 200))
                return AgentApiResult(
                    node_id=target.node_id,
                    action=command.action.value,
                    operation=command.operation,
                    accepted=200 <= status_code < 300,
                    status_code=status_code,
                    message=str(parsed.get("message", "accepted")),
                    request_id=command.request_id,
                    response=parsed,
                )
        except HTTPError as exc:
            return AgentApiResult(
                node_id=target.node_id,
                action=command.action.value,
                operation=command.operation,
                accepted=False,
                status_code=int(exc.code),
                message=str(exc.reason),
                request_id=command.request_id,
                response={},
            )
        except URLError as exc:
            return AgentApiResult(
                node_id=target.node_id,
                action=command.action.value,
                operation=command.operation,
                accepted=False,
                status_code=0,
                message=str(exc.reason),
                request_id=command.request_id,
                response={},
            )
