from __future__ import annotations

from dnsforge.application.validate.settings_factory import ProxySettingsFactory
from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class ValidateProxy:
    def __init__(self, paths: ProjectPaths, factory: ProxySettingsFactory | None = None) -> None:
        self.paths = paths
        self.factory = factory or ProxySettingsFactory(paths)

    def execute(self, node: str, proxy_type: ProxyType) -> None:
        self.factory.build(node, proxy_type)
