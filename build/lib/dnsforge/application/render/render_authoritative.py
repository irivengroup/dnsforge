from __future__ import annotations

from dnsforge.application.validate.settings_factory import AuthoritativeSettingsFactory
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.infrastructure.rendering.bind_renderer import BindRenderTree


class RenderAuthoritative:
    def __init__(
        self,
        paths: ProjectPaths,
        factory: AuthoritativeSettingsFactory | None = None,
        renderer: BindRenderTree | None = None,
    ) -> None:
        self.paths = paths
        self.factory = factory or AuthoritativeSettingsFactory(paths)
        self.renderer = renderer or BindRenderTree()

    def execute(self, node: str) -> None:
        settings = self.factory.build(node)
        destination = self.paths.project_root / "src" / "render" / "dns-authoritative" / node
        self.renderer.render_authoritative(settings, destination)
