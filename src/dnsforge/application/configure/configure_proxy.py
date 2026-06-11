from __future__ import annotations

from dnsforge.application.configure.configure_planner import ConfigurePlanner
from dnsforge.application.configure.configure_service import ConfigureService
from dnsforge.application.render.render_proxy import RenderProxy
from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.model.roles import DnsRole
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class ConfigureProxy:
    def __init__(
        self,
        paths: ProjectPaths,
        renderer: RenderProxy | None = None,
        planner: ConfigurePlanner | None = None,
        service: ConfigureService | None = None,
    ) -> None:
        self.paths = paths
        self.renderer = renderer or RenderProxy(paths)
        self.planner = planner or ConfigurePlanner()
        self.service = service or ConfigureService()

    def execute(
        self,
        node: str,
        proxy_type: ProxyType,
        render_only: bool = False,
        skip_install: bool = False,
        dry_run: bool = False,
    ) -> None:
        self.renderer.execute(node, proxy_type)
        render_root = self.paths.render_dir(DnsRole.PROXY, node)
        plan = self.planner.build_proxy_plan(node, proxy_type.value, render_root, dry_run, skip_install)
        print(plan.summary())

        if render_only:
            return

        self.service.apply(plan)
