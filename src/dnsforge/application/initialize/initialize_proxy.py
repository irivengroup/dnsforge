from __future__ import annotations

from dnsforge.application.initialize.initialize_planner import InitializePlanner
from dnsforge.application.initialize.initialize_service import InitializeService
from dnsforge.application.render.render_proxy import RenderProxy
from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.model.roles import DnsRole
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class InitializeProxy:
    def __init__(
        self,
        paths: ProjectPaths,
        renderer: RenderProxy | None = None,
        planner: InitializePlanner | None = None,
        service: InitializeService | None = None,
    ) -> None:
        self.paths = paths
        self.renderer = renderer or RenderProxy(paths)
        self.planner = planner or InitializePlanner()
        self.service = service or InitializeService()

    def execute(
        self,
        node: str,
        proxy_type: ProxyType,
        render_only: bool = False,
        backup_before_apply: bool = True,
        dry_run: bool = False,
        apply_only: bool = False,
    ) -> None:
        self.service.assert_not_initialized(self.paths.setup_file)

        if not apply_only:
            self.renderer.execute(node, proxy_type)
        render_root = self.paths.render_dir(DnsRole.PROXY, node)
        plan = self.planner.build_proxy_plan(node, proxy_type.value, render_root, dry_run, backup_before_apply)
        print(plan.summary())

        if render_only:
            return

        self.service.apply(plan, setup_file=self.paths.setup_file)
