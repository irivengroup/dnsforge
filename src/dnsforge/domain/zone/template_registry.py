from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dnsforge.domain.zone.policy_validator import ServerProfile, ZonePolicyKey, ZonePolicyValidator, ZoneScope
from dnsforge.domain.zone.model import ZoneType


@dataclass(frozen=True)
class ZoneTemplateKey:
    profile: ServerProfile
    scope: ZoneScope
    zone_type: ZoneType

    def policy_key(self) -> ZonePolicyKey:
        return ZonePolicyKey(self.profile, self.scope, self.zone_type)


@dataclass(frozen=True)
class ZoneTemplateArtifact:
    key: ZoneTemplateKey
    template: Path
    destination_name: str


class ZoneTemplateRegistry:
    """Registry for zone declaration templates by profile, scope and type."""

    @classmethod
    def artifacts(cls) -> tuple[ZoneTemplateArtifact, ...]:
        artifacts: list[ZoneTemplateArtifact] = []
        for profile in ServerProfile:
            for scope in ZoneScope:
                for zone_type in sorted(
                    ZonePolicyValidator.allowed_types(profile, scope), key=lambda item: item.value
                ):
                    key = ZoneTemplateKey(profile, scope, zone_type)
                    artifacts.append(
                        ZoneTemplateArtifact(
                            key=key,
                            template=cls.template_path(key),
                            destination_name=cls.destination_name(zone_type),
                        )
                    )
        return tuple(artifacts)

    @staticmethod
    def template_path(key: ZoneTemplateKey) -> Path:
        ZonePolicyValidator.validate_key(key.policy_key())
        return Path("zones") / key.profile.value / key.scope.value / f"{key.zone_type.value}.conf.tpl"

    @staticmethod
    def destination_name(zone_type: ZoneType) -> str:
        return f"{zone_type.value}.conf.tpl"

    @classmethod
    def templates(cls) -> tuple[Path, ...]:
        return tuple(artifact.template for artifact in cls.artifacts())

    @classmethod
    def by_key(cls, key: ZoneTemplateKey) -> ZoneTemplateArtifact:
        ZonePolicyValidator.validate_key(key.policy_key())
        for artifact in cls.artifacts():
            if artifact.key == key:
                return artifact
        raise KeyError(key)
