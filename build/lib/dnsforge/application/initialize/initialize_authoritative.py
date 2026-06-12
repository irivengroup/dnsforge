from __future__ import annotations

from dnsforge.application.initialize.initialize_planner import InitializePlanner
from dnsforge.application.initialize.initialize_service import InitializeService
from dnsforge.application.render.render_authoritative import RenderAuthoritative
from dnsforge.domain.model.roles import DnsRole
from dnsforge.domain.profile.model import ConfigurationProfile
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.infrastructure.profile.setup_template_service import ProfileSetupTemplateService


class InitializeAuthoritative:
    def __init__(
        self,
        paths: ProjectPaths,
        renderer: RenderAuthoritative | None = None,
        planner: InitializePlanner | None = None,
        service: InitializeService | None = None,
        setup_templates: ProfileSetupTemplateService | None = None,
    ) -> None:
        self.paths = paths
        self.renderer = renderer or RenderAuthoritative(paths)
        self.planner = planner or InitializePlanner()
        self.service = service or InitializeService()
        self.setup_templates = setup_templates or ProfileSetupTemplateService()

    def execute(
        self,
        node: str,
        render_only: bool = False,
        backup_before_apply: bool = True,
        dry_run: bool = False,
        apply_only: bool = False,
    ) -> None:
        self.service.assert_not_initialized(self.paths.setup_file)
        self.setup_templates.ensure_setup_file(
            ConfigurationProfile.AUTHORITATIVE,
            self.paths.setup_file,
            node=node,
            dry_run=dry_run,
        )

        if not apply_only:
            self.renderer.execute(node)
        render_root = self.paths.render_dir(DnsRole.AUTHORITATIVE, node)
        plan = self.planner.build_authoritative_plan(node, render_root, dry_run, backup_before_apply)
        print(plan.summary())

        if render_only:
            return

        self.service.apply(plan, setup_file=self.paths.setup_file)
