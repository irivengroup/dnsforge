from __future__ import annotations

from dnsforge.application.validate.settings_factory import AuthoritativeSettingsFactory
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class ValidateAuthoritative:
    def __init__(self, paths: ProjectPaths, factory: AuthoritativeSettingsFactory | None = None) -> None:
        self.paths = paths
        self.factory = factory or AuthoritativeSettingsFactory(paths)

    def execute(self, node: str) -> None:
        self.factory.build(node)
