from __future__ import annotations

import hashlib
import secrets
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum


class AgentTrustState(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REVOKED = "revoked"


@dataclass(frozen=True)
class AgentCertificate:
    fingerprint: str
    public_key: str
    issuer: str = "dnsforge-manager"
    serial_number: str = ""
    subject: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    revoked_at: str | None = None

    def __post_init__(self) -> None:
        if self.fingerprint != certificate_fingerprint(self.public_key):
            raise ValueError("certificate fingerprint does not match public key")

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "AgentCertificate":
        return cls(
            fingerprint=str(data["fingerprint"]),
            public_key=str(data["public_key"]),
            issuer=str(data.get("issuer", "dnsforge-manager")),
            serial_number=str(data.get("serial_number", "")),
            subject=str(data.get("subject", "")),
            created_at=str(data.get("created_at", datetime.now(timezone.utc).isoformat())),
            revoked_at=None if data.get("revoked_at") is None else str(data.get("revoked_at")),
        )


@dataclass(frozen=True)
class EnrollmentRequest:
    request_id: str
    fingerprint: str
    hostname: str
    version: str
    profile: str
    site: str = "default"
    cluster: str | None = None
    public_key: str = ""
    status: AgentTrustState = AgentTrustState.PENDING
    requested_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    approved_at: str | None = None
    revoked_at: str | None = None
    labels: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "EnrollmentRequest":
        labels = data.get("labels", {})
        if not isinstance(labels, dict):
            raise ValueError("enrollment labels must be a mapping")
        return cls(
            request_id=str(data["request_id"]),
            fingerprint=str(data["fingerprint"]),
            hostname=str(data["hostname"]),
            version=str(data.get("version", "")),
            profile=str(data.get("profile", "")),
            site=str(data.get("site", "default")),
            cluster=None if data.get("cluster") is None else str(data.get("cluster")),
            public_key=str(data.get("public_key", "")),
            status=AgentTrustState(str(data.get("status", AgentTrustState.PENDING.value))),
            requested_at=str(data.get("requested_at", datetime.now(timezone.utc).isoformat())),
            approved_at=None if data.get("approved_at") is None else str(data.get("approved_at")),
            revoked_at=None if data.get("revoked_at") is None else str(data.get("revoked_at")),
            labels={str(key): str(value) for key, value in labels.items()},
        )


@dataclass(frozen=True)
class TrustedAgent:
    fingerprint: str
    hostname: str
    version: str
    profile: str
    site: str = "default"
    cluster: str | None = None
    state: AgentTrustState = AgentTrustState.PENDING
    certificate: AgentCertificate | None = None
    token: str | None = field(default=None, compare=False)
    approved_at: str | None = None
    revoked_at: str | None = None
    labels: dict[str, str] = field(default_factory=dict)

    def to_dict(self, *, include_token: bool = False) -> dict[str, object]:
        data = asdict(self)
        data["state"] = self.state.value
        if self.certificate is not None:
            data["certificate"] = self.certificate.to_dict()
        if not include_token:
            data.pop("token", None)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "TrustedAgent":
        labels = data.get("labels", {})
        if not isinstance(labels, dict):
            raise ValueError("trusted agent labels must be a mapping")
        certificate = data.get("certificate")
        if certificate is not None and not isinstance(certificate, dict):
            raise ValueError("trusted agent certificate must be an object")
        return cls(
            fingerprint=str(data["fingerprint"]),
            hostname=str(data["hostname"]),
            version=str(data.get("version", "")),
            profile=str(data.get("profile", "")),
            site=str(data.get("site", "default")),
            cluster=None if data.get("cluster") is None else str(data.get("cluster")),
            state=AgentTrustState(str(data.get("state", AgentTrustState.PENDING.value))),
            certificate=None if certificate is None else AgentCertificate.from_dict(certificate),
            token=None if data.get("token") is None else str(data.get("token")),
            approved_at=None if data.get("approved_at") is None else str(data.get("approved_at")),
            revoked_at=None if data.get("revoked_at") is None else str(data.get("revoked_at")),
            labels={str(key): str(value) for key, value in labels.items()},
        )


@dataclass(frozen=True)
class NodeApprovalDecision:
    node_id: str
    approved: bool
    fingerprint: str | None = None
    message: str = ""


def certificate_fingerprint(public_key: str) -> str:
    return hashlib.sha256(public_key.encode("utf-8")).hexdigest()


def new_agent_token() -> str:
    return secrets.token_urlsafe(32)
