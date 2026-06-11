from __future__ import annotations

from dnsforge.application.validate.settings_factory import ProxySettingsFactory
from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.infrastructure.rendering.bind_renderer import BindRenderTree


class RenderProxy:
    def __init__(self, paths: ProjectPaths, factory: ProxySettingsFactory | None = None, renderer: BindRenderTree | None = None) -> None:
        self.paths = paths
        self.factory = factory or ProxySettingsFactory(paths)
        self.renderer = renderer or BindRenderTree()

    def execute(self, node: str, proxy_type: ProxyType) -> None:
        settings = self.factory.build(node, proxy_type)
        destination = self.paths.project_root / "src" / "render" / "dns-proxy" / node
        self.renderer.render_proxy(settings, destination)
