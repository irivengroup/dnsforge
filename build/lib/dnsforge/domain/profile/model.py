from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConfigurationProfile(str, Enum):
    AUTHORITATIVE = "authoritative"
    PROXY_FORWARDER = "proxy-forwarder"
    PROXY_HYBRID = "proxy-hybrid"

    @classmethod
    def choices(cls) -> list[str]:
        return [item.value for item in cls]

    @classmethod
    def from_value(cls, value: str) -> "ConfigurationProfile":
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"invalid configuration profile: {value}")

    @property
    def role(self) -> str:
        if self is ConfigurationProfile.AUTHORITATIVE:
            return "dns-authoritative"
        return "dns-proxy"

    @property
    def proxy_type(self) -> str | None:
        if self is ConfigurationProfile.PROXY_FORWARDER:
            return "forwarder"
        if self is ConfigurationProfile.PROXY_HYBRID:
            return "hybrid"
        return None


@dataclass(frozen=True)
class ProfilePolicy:
    profile: ConfigurationProfile

    @property
    def rpz_allowed(self) -> bool:
        return self.profile is not ConfigurationProfile.AUTHORITATIVE

    @property
    def local_proxy_zones_allowed(self) -> bool:
        return self.profile is ConfigurationProfile.PROXY_HYBRID

    @property
    def requires_proxy_type(self) -> bool:
        return self.profile is not ConfigurationProfile.AUTHORITATIVE
