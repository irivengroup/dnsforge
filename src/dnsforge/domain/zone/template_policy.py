from __future__ import annotations

from pathlib import Path

from dnsforge.domain.zone.template_registry import ZoneTemplateKey, ZoneTemplateRegistry
from dnsforge.domain.zone.policy_validator import ServerProfile, ZoneScope


class ZoneTemplatePolicy:
    """Backward-free policy facade for selecting zone templates."""

    @staticmethod
    def template_path(key: ZoneTemplateKey) -> Path:
        return ZoneTemplateRegistry.template_path(key)


__all__ = ["ServerProfile", "ZoneScope", "ZoneTemplateKey", "ZoneTemplatePolicy", "ZoneTemplateRegistry"]
