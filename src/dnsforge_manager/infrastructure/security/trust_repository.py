from __future__ import annotations

import json
from pathlib import Path

from dnsforge_manager.domain.security.models import EnrollmentRequest, TrustedAgent


class AgentTrustRepository:
    def save_enrollment(self, request: EnrollmentRequest) -> EnrollmentRequest:
        raise NotImplementedError

    def get_enrollment(self, request_id: str) -> EnrollmentRequest:
        raise NotImplementedError

    def list_enrollments(self) -> tuple[EnrollmentRequest, ...]:
        raise NotImplementedError

    def save_agent(self, agent: TrustedAgent) -> TrustedAgent:
        raise NotImplementedError

    def get_agent(self, fingerprint: str) -> TrustedAgent:
        raise NotImplementedError

    def list_agents(self) -> tuple[TrustedAgent, ...]:
        raise NotImplementedError


class InMemoryAgentTrustRepository(AgentTrustRepository):
    def __init__(self) -> None:
        self._enrollments: dict[str, EnrollmentRequest] = {}
        self._agents: dict[str, TrustedAgent] = {}

    def save_enrollment(self, request: EnrollmentRequest) -> EnrollmentRequest:
        self._enrollments[request.request_id] = request
        return request

    def get_enrollment(self, request_id: str) -> EnrollmentRequest:
        try:
            return self._enrollments[request_id]
        except KeyError as exc:
            raise KeyError(f"unknown enrollment request: {request_id}") from exc

    def list_enrollments(self) -> tuple[EnrollmentRequest, ...]:
        return tuple(self._enrollments[key] for key in sorted(self._enrollments))

    def save_agent(self, agent: TrustedAgent) -> TrustedAgent:
        self._agents[agent.fingerprint] = agent
        return agent

    def get_agent(self, fingerprint: str) -> TrustedAgent:
        try:
            return self._agents[fingerprint]
        except KeyError as exc:
            raise KeyError(f"unknown trusted agent: {fingerprint}") from exc

    def list_agents(self) -> tuple[TrustedAgent, ...]:
        return tuple(self._agents[key] for key in sorted(self._agents))


class JsonAgentTrustRepository(AgentTrustRepository):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read(self) -> dict[str, list[dict[str, object]]]:
        if not self.path.exists():
            return {"enrollments": [], "trusted_agents": []}
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(f"{self.path} must contain a JSON object")
        return {
            "enrollments": _list(raw.get("enrollments", [])),
            "trusted_agents": _list(raw.get("trusted_agents", [])),
        }

    def _write(self, data: dict[str, list[dict[str, object]]]) -> None:
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(self.path)

    def _upsert(self, key: str, identifier: str, payload: dict[str, object]) -> None:
        data = self._read()
        value = str(payload[identifier])
        data[key] = [item for item in data[key] if str(item.get(identifier)) != value]
        data[key].append(payload)
        data[key] = sorted(data[key], key=lambda item: str(item.get(identifier, "")))
        self._write(data)

    def save_enrollment(self, request: EnrollmentRequest) -> EnrollmentRequest:
        self._upsert("enrollments", "request_id", request.to_dict())
        return request

    def get_enrollment(self, request_id: str) -> EnrollmentRequest:
        for item in self._read()["enrollments"]:
            if str(item.get("request_id")) == request_id:
                return EnrollmentRequest.from_dict(item)
        raise KeyError(f"unknown enrollment request: {request_id}")

    def list_enrollments(self) -> tuple[EnrollmentRequest, ...]:
        return tuple(EnrollmentRequest.from_dict(item) for item in self._read()["enrollments"])

    def save_agent(self, agent: TrustedAgent) -> TrustedAgent:
        self._upsert("trusted_agents", "fingerprint", agent.to_dict(include_token=True))
        return agent

    def get_agent(self, fingerprint: str) -> TrustedAgent:
        for item in self._read()["trusted_agents"]:
            if str(item.get("fingerprint")) == fingerprint:
                return TrustedAgent.from_dict(item)
        raise KeyError(f"unknown trusted agent: {fingerprint}")

    def list_agents(self) -> tuple[TrustedAgent, ...]:
        return tuple(TrustedAgent.from_dict(item) for item in self._read()["trusted_agents"])


def _list(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        raise ValueError("trust repository collections must be lists")
    result: list[dict[str, object]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("trust repository entries must be JSON objects")
        result.append(item)
    return result
