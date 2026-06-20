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
class AgentTrustPolicy:
    policy_id: str
    name: str
    allowed_profiles: tuple[str, ...] = ()
    allowed_sites: tuple[str, ...] = ()
    require_public_key: bool = True
    auto_approve: bool = False
    max_token_age_days: int = 90
    certificate_rotation_days: int = 180
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def allows(self, request: "EnrollmentRequest") -> bool:
        if self.require_public_key and not request.public_key:
            return False
        if self.allowed_profiles and request.profile not in self.allowed_profiles:
            return False
        return not (self.allowed_sites and request.site not in self.allowed_sites)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["allowed_profiles"] = list(self.allowed_profiles)
        data["allowed_sites"] = list(self.allowed_sites)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "AgentTrustPolicy":
        return cls(
            policy_id=str(data["policy_id"]),
            name=str(data.get("name", data["policy_id"])),
            allowed_profiles=_string_tuple(data.get("allowed_profiles", ())),
            allowed_sites=_string_tuple(data.get("allowed_sites", ())),
            require_public_key=bool(data.get("require_public_key", True)),
            auto_approve=bool(data.get("auto_approve", False)),
            max_token_age_days=_int_value(data.get("max_token_age_days", 90)),
            certificate_rotation_days=_int_value(data.get("certificate_rotation_days", 180)),
            created_at=str(data.get("created_at", datetime.now(timezone.utc).isoformat())),
        )


@dataclass(frozen=True)
class AgentRotationRecord:
    rotation_id: str
    fingerprint: str
    rotated_at: str
    reason: str = "operator-request"
    previous_token_digest: str = ""
    certificate_rotated: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "AgentRotationRecord":
        return cls(
            rotation_id=str(data["rotation_id"]),
            fingerprint=str(data["fingerprint"]),
            rotated_at=str(data.get("rotated_at", datetime.now(timezone.utc).isoformat())),
            reason=str(data.get("reason", "operator-request")),
            previous_token_digest=str(data.get("previous_token_digest", "")),
            certificate_rotated=bool(data.get("certificate_rotated", False)),
        )


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


def _int_value(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, str, bytes, bytearray)):
        return int(value)
    raise ValueError("expected integer-compatible value")


def _string_tuple(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(item.strip() for item in value.split(",") if item.strip())
    if not isinstance(value, (list, tuple, set)):
        raise ValueError("expected a string collection")
    return tuple(str(item) for item in value)


def token_digest(token: str | None) -> str:
    if not token:
        return ""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def certificate_fingerprint(public_key: str) -> str:
    return hashlib.sha256(public_key.encode("utf-8")).hexdigest()


def new_agent_token() -> str:
    return secrets.token_urlsafe(32)
