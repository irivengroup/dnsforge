from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class SecurityProfile(str, Enum):
    STANDARD = "standard"
    HARDENED = "hardened"
    ENTERPRISE = "enterprise"
    PARANOID = "paranoid"

    @classmethod
    def choices(cls) -> list[str]:
        return [item.value for item in cls]

    @classmethod
    def from_value(cls, value: str | None) -> "SecurityProfile":
        normalized = (value or "enterprise").strip().strip("\"'").lower()
        for item in cls:
            if item.value == normalized:
                return item
        raise ValueError(f"invalid security profile: {value}")

    @property
    def weight(self) -> int:
        return {self.STANDARD: 1, self.HARDENED: 2, self.ENTERPRISE: 3, self.PARANOID: 4}[self]


@dataclass(frozen=True)
class SecurityControls:
    profile: SecurityProfile
    hide_version: bool = True
    minimal_responses: bool = True
    minimal_any: bool = True
    dns_cookies: bool = True
    rrl: bool = True
    dnssec_validation: bool = True
    qname_minimization: bool = True
    serve_stale: bool = True
    strict_acl: bool = True
    rpz_required: bool = False
    systemd_hardening: bool = True
    firewall: bool = True
    selinux: bool = True

    @classmethod
    def from_profile(cls, profile: SecurityProfile) -> "SecurityControls":
        if profile is SecurityProfile.STANDARD:
            return cls(
                profile,
                rrl=False,
                qname_minimization=False,
                serve_stale=False,
                strict_acl=False,
                systemd_hardening=False,
                firewall=False,
                selinux=False,
            )
        if profile is SecurityProfile.HARDENED:
            return cls(profile, serve_stale=False, systemd_hardening=False)
        if profile is SecurityProfile.PARANOID:
            return cls(profile, rpz_required=True)
        return cls(profile)

    def enabled_controls(self) -> dict[str, bool]:
        return {k: v for k, v in self.__dict__.items() if k != "profile"}

    def score(self) -> int:
        values = list(self.enabled_controls().values())
        return int(sum(1 for value in values if value) * 100 / len(values))
