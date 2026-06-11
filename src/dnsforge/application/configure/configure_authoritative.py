from __future__ import annotations

from dnsforge.application.configure.configure_planner import ConfigurePlanner
from dnsforge.application.configure.configure_service import ConfigureService
from dnsforge.application.render.render_authoritative import RenderAuthoritative
from dnsforge.domain.model.roles import DnsRole
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class ConfigureAuthoritative:
    def __init__(
        self,
        paths: ProjectPaths,
        renderer: RenderAuthoritative | None = None,
        planner: ConfigurePlanner | None = None,
        service: ConfigureService | None = None,
    ) -> None:
        self.paths = paths
        self.renderer = renderer or RenderAuthoritative(paths)
        self.planner = planner or ConfigurePlanner()
        self.service = service or ConfigureService()

    def execute(
        self,
        node: str,
        render_only: bool = False,
        skip_install: bool = False,
        dry_run: bool = False,
    ) -> None:
        self.renderer.execute(node)
        render_root = self.paths.render_dir(DnsRole.AUTHORITATIVE, node)
        plan = self.planner.build_authoritative_plan(node, render_root, dry_run, skip_install)
        print(plan.summary())

        if render_only:
            return

        self.service.apply(plan)
