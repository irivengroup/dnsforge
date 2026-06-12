from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from dnsforge.domain.zone.model import ZoneType


class ZoneScope(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"

    @classmethod
    def from_value(cls, value: str) -> "ZoneScope":
        normalized = value.strip().lower()
        for item in cls:
            if item.value == normalized:
                return item
        raise ValueError(f"unsupported zone scope: {value}")


class ServerProfile(str, Enum):
    AUTHORITATIVE = "authoritative"
    PROXY_FORWARDER = "proxy-forwarder"
    PROXY_HYBRID = "proxy-hybrid"

    @classmethod
    def from_value(cls, value: str) -> "ServerProfile":
        normalized = value.strip().lower()
        for item in cls:
            if item.value == normalized:
                return item
        raise ValueError(f"unsupported server profile: {value}")


@dataclass(frozen=True)
class ZoneTemplateKey:
    profile: ServerProfile
    scope: ZoneScope
    zone_type: ZoneType


class ZoneTemplatePolicy:
    """Selects zone configuration templates by server profile and scope.

    The resource tree intentionally keeps a dedicated template for each
    profile/scope/type combination. Some files are currently identical, but the
    separation prevents future Enterprise DNS policy changes from leaking across
    authoritative, forwarder and hybrid deployments.
    """

    @staticmethod
    def template_path(key: ZoneTemplateKey) -> Path:
        return Path("zones") / key.profile.value / key.scope.value / f"{key.zone_type.value}.conf.tpl"
