from __future__ import annotations

import hashlib
import secrets
from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

from dnsforge_manager.domain.inventory.models import ManagedNode, NodeStatus
from dnsforge_manager.domain.security.models import (
    AgentCertificate,
    AgentRotationRecord,
    AgentTrustPolicy,
    AgentTrustState,
    EnrollmentRequest,
    NodeApprovalDecision,
    TrustedAgent,
    certificate_fingerprint,
    new_agent_token,
    token_digest,
)
from dnsforge_manager.infrastructure.inventory.repository import NodeInventoryRepository
from dnsforge_manager.infrastructure.security.trust_repository import AgentTrustRepository, InMemoryAgentTrustRepository


class AgentTrustService:
    """Trust model for Manager-to-DNSForge-agent relationships.

    v14.3.0 introduces an explicit Agent Trust Framework while keeping the v14.x node trust API backward
    compatible. The Manager records enrollment requests, approves/revokes trusted agents and never exposes stored
    tokens unless the caller explicitly receives an approval/rotation response.
    """

    def __init__(
        self,
        repository: NodeInventoryRepository | None = None,
        trust_repository: AgentTrustRepository | None = None,
    ) -> None:
        self.repository = repository
        self.trust_repository = trust_repository or InMemoryAgentTrustRepository()

    @staticmethod
    def fingerprint_for(endpoint: str, public_key: str = "") -> str:
        material = f"{endpoint}|{public_key}".encode("utf-8")
        return hashlib.sha256(material).hexdigest()

    def enroll(self, payload: dict[str, object]) -> EnrollmentRequest:
        public_key = str(payload.get("public_key", ""))
        fingerprint = str(payload.get("fingerprint") or certificate_fingerprint(public_key or str(payload["hostname"])))
        request = EnrollmentRequest(
            request_id=str(payload.get("request_id") or uuid4()),
            fingerprint=fingerprint,
            hostname=str(payload["hostname"]),
            version=str(payload.get("version", "")),
            profile=str(payload.get("profile", "")),
            site=str(payload.get("site", "default")),
            cluster=None if payload.get("cluster") is None else str(payload.get("cluster")),
            public_key=public_key,
            labels=_labels(payload.get("labels", {})),
        )
        return self.trust_repository.save_enrollment(request)

    def list_enrollments(self) -> tuple[EnrollmentRequest, ...]:
        return self.trust_repository.list_enrollments()

    def list_trusted_agents(self) -> tuple[TrustedAgent, ...]:
        return self.trust_repository.list_agents()

    def approve_enrollment(self, request_id: str) -> TrustedAgent:
        request = self.trust_repository.get_enrollment(request_id)
        if request.status == AgentTrustState.REVOKED:
            raise ValueError(f"cannot approve revoked enrollment request: {request_id}")
        now = datetime.now(timezone.utc).isoformat()
        certificate = None
        if request.public_key:
            certificate = AgentCertificate(
                fingerprint=request.fingerprint,
                public_key=request.public_key,
                serial_number=request.request_id,
                subject=request.hostname,
                created_at=now,
            )
        approved_request = replace(request, status=AgentTrustState.APPROVED, approved_at=now)
        agent = TrustedAgent(
            fingerprint=request.fingerprint,
            hostname=request.hostname,
            version=request.version,
            profile=request.profile,
            site=request.site,
            cluster=request.cluster,
            state=AgentTrustState.APPROVED,
            certificate=certificate,
            token=new_agent_token(),
            approved_at=now,
            labels=request.labels,
        )
        self.trust_repository.save_enrollment(approved_request)
        return self.trust_repository.save_agent(agent)

    def revoke_trusted_agent(self, fingerprint: str) -> TrustedAgent:
        agent = self.trust_repository.get_agent(fingerprint)
        now = datetime.now(timezone.utc).isoformat()
        certificate = None if agent.certificate is None else replace(agent.certificate, revoked_at=now)
        revoked = replace(
            agent,
            state=AgentTrustState.REVOKED,
            certificate=certificate,
            token=None,
            revoked_at=now,
        )
        return self.trust_repository.save_agent(revoked)

    def rotate_trusted_agent_token(self, fingerprint: str, *, reason: str = "token-rotation") -> TrustedAgent:
        agent = self.trust_repository.get_agent(fingerprint)
        if agent.state == AgentTrustState.REVOKED:
            raise ValueError(f"cannot rotate token for revoked trusted agent: {fingerprint}")
        now = datetime.now(timezone.utc).isoformat()
        rotated = self.trust_repository.save_agent(replace(agent, token=new_agent_token()))
        self.trust_repository.save_rotation(
            AgentRotationRecord(
                rotation_id=str(uuid4()),
                fingerprint=fingerprint,
                rotated_at=now,
                reason=reason,
                previous_token_digest=token_digest(agent.token),
                certificate_rotated=False,
            )
        )
        return rotated

    def create_policy(self, payload: dict[str, object]) -> AgentTrustPolicy:
        policy = AgentTrustPolicy(
            policy_id=str(payload["policy_id"]),
            name=str(payload.get("name", payload["policy_id"])),
            allowed_profiles=_tuple_payload(payload.get("allowed_profiles", ())),
            allowed_sites=_tuple_payload(payload.get("allowed_sites", ())),
            require_public_key=_bool_payload(payload.get("require_public_key", True)),
            auto_approve=_bool_payload(payload.get("auto_approve", False)),
            max_token_age_days=_int_payload(payload.get("max_token_age_days", 90)),
            certificate_rotation_days=_int_payload(payload.get("certificate_rotation_days", 180)),
        )
        return self.trust_repository.save_policy(policy)

    def list_policies(self) -> tuple[AgentTrustPolicy, ...]:
        return self.trust_repository.list_policies()

    def list_rotations(self, fingerprint: str | None = None) -> tuple[AgentRotationRecord, ...]:
        return self.trust_repository.list_rotations(fingerprint)

    def evaluate_enrollment(self, request_id: str, policy_id: str) -> dict[str, object]:
        request = self.trust_repository.get_enrollment(request_id)
        policy = self.trust_repository.get_policy(policy_id)
        allowed = policy.allows(request)
        return {
            "request_id": request.request_id,
            "policy_id": policy.policy_id,
            "allowed": allowed,
            "auto_approve": policy.auto_approve and allowed,
        }

    def rotate_trusted_agent_certificate(
        self,
        fingerprint: str,
        *,
        public_key: str | None = None,
        reason: str = "certificate-rotation",
    ) -> TrustedAgent:
        agent = self.trust_repository.get_agent(fingerprint)
        if agent.state == AgentTrustState.REVOKED:
            raise ValueError(f"cannot rotate certificate for revoked trusted agent: {fingerprint}")
        now = datetime.now(timezone.utc).isoformat()
        key = public_key or (agent.certificate.public_key if agent.certificate is not None else "")
        certificate = None
        if key:
            certificate = AgentCertificate(
                fingerprint=certificate_fingerprint(key),
                public_key=key,
                serial_number=str(uuid4()),
                subject=agent.hostname,
                created_at=now,
            )
        updated = replace(
            agent, fingerprint=certificate.fingerprint if certificate else agent.fingerprint, certificate=certificate
        )
        saved = self.trust_repository.save_agent(updated)
        self.trust_repository.save_rotation(
            AgentRotationRecord(
                rotation_id=str(uuid4()),
                fingerprint=saved.fingerprint,
                rotated_at=now,
                reason=reason,
                previous_token_digest=token_digest(agent.token),
                certificate_rotated=True,
            )
        )
        return saved

    def register_pending(self, node: ManagedNode, *, public_key: str = "") -> ManagedNode:
        if self.repository is None:
            raise RuntimeError("legacy node trust repository is not configured")
        fingerprint = node.agent_fingerprint or self.fingerprint_for(node.api_endpoint, public_key)
        pending = replace(
            node,
            agent_fingerprint=fingerprint,
            trust_state=AgentTrustState.PENDING.value,
            status=NodeStatus.REGISTERED,
        )
        return self.repository.register(pending)

    def approve_node(self, node_id: str) -> NodeApprovalDecision:
        if self.repository is None:
            raise RuntimeError("legacy node trust repository is not configured")
        node = self.repository.get(node_id)
        fingerprint = node.agent_fingerprint or self.fingerprint_for(node.api_endpoint)
        approved = replace(
            node,
            agent_fingerprint=fingerprint,
            trust_state=AgentTrustState.APPROVED.value,
            status=NodeStatus.ACTIVE,
        )
        self.repository.upsert(approved)
        return NodeApprovalDecision(node_id=node_id, approved=True, fingerprint=fingerprint, message="approved")

    def revoke_node(self, node_id: str) -> ManagedNode:
        if self.repository is None:
            raise RuntimeError("legacy node trust repository is not configured")
        node = self.repository.get(node_id)
        revoked = replace(node, trust_state=AgentTrustState.REVOKED.value, status=NodeStatus.DISABLED, agent_token=None)
        return self.repository.upsert(revoked)

    def rotate_token(self, node_id: str) -> ManagedNode:
        if self.repository is None:
            raise RuntimeError("legacy node trust repository is not configured")
        node = self.repository.get(node_id)
        if node.trust_state == AgentTrustState.REVOKED.value:
            raise ValueError(f"cannot rotate token for revoked node: {node_id}")
        return self.repository.upsert(replace(node, agent_token=secrets.token_urlsafe(32)))

    @staticmethod
    def assert_trusted(node: ManagedNode) -> None:
        if node.trust_state != AgentTrustState.APPROVED.value:
            raise PermissionError(f"node is not approved for Manager operations: {node.node_id}")
        if node.status in {NodeStatus.DISABLED, NodeStatus.UNREACHABLE}:
            raise PermissionError(f"node is not active for Manager operations: {node.node_id}")


def _labels(value: object) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("labels must be a mapping")
    return {str(key): str(item) for key, item in value.items()}


def _tuple_payload(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(item.strip() for item in value.split(",") if item.strip())
    if not isinstance(value, (list, tuple, set)):
        raise ValueError("trust policy collection fields must be strings or lists")
    return tuple(str(item) for item in value)


def _bool_payload(value: object) -> bool:
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _int_payload(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, str, bytes, bytearray)):
        return int(value)
    raise ValueError("trust policy integer fields must be integer-compatible")
