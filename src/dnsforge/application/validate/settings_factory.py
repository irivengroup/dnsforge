from __future__ import annotations

from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.model.roles import DnsRole
from dnsforge.domain.model.settings import AuthoritativeSettings, ProxySettings
from dnsforge.domain.services.settings_validator import AuthoritativeSettingsValidator, ProxySettingsValidator
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader


class ProxySettingsFactory:
    def __init__(self, paths: ProjectPaths, loader: EnvSettingsLoader | None = None, validator: ProxySettingsValidator | None = None) -> None:
        self.paths = paths
        self.loader = loader or EnvSettingsLoader()
        self.validator = validator or ProxySettingsValidator()

    def build(self, node: str, proxy_type: ProxyType) -> ProxySettings:
        raw = self.loader.load(self.paths.settings_file(DnsRole.PROXY, node))
        raw["ROLE"] = DnsRole.PROXY.value
        raw["NODE_NAME"] = node
        raw["PROXY_TYPE"] = proxy_type.value
        self.validator.validate(raw)
        return ProxySettings(role=DnsRole.PROXY, node_name=node, proxy_type=proxy_type, raw=raw)


class AuthoritativeSettingsFactory:
    def __init__(self, paths: ProjectPaths, loader: EnvSettingsLoader | None = None, validator: AuthoritativeSettingsValidator | None = None) -> None:
        self.paths = paths
        self.loader = loader or EnvSettingsLoader()
        self.validator = validator or AuthoritativeSettingsValidator()

    def build(self, node: str) -> AuthoritativeSettings:
        raw = self.loader.load(self.paths.settings_file(DnsRole.AUTHORITATIVE, node))
        raw["ROLE"] = DnsRole.AUTHORITATIVE.value
        raw["NODE_NAME"] = node
        self.validator.validate(raw)
        return AuthoritativeSettings(role=DnsRole.AUTHORITATIVE, node_name=node, raw=raw)
