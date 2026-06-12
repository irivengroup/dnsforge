from __future__ import annotations

from dnsforge.application.initialize.initialize_planner import InitializePlanner
from dnsforge.application.initialize.initialize_service import InitializeService
from dnsforge.application.render.render_authoritative import RenderAuthoritative
from dnsforge.application.render.render_proxy import RenderProxy
from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.model.roles import DnsRole
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader
from dnsforge.shared.errors import SettingsError


class InitializeCommand:
    """Initialize BIND from the already-installed DNSForge setup.conf.

    The installation scripts select the server profile and deploy
    /etc/dnsforge/setup.conf. This command only consumes that edited source of
    truth, renders the matching BIND tree, applies it when requested and creates
    the one-shot initialization lock.
    """

    def __init__(
        self,
        paths: ProjectPaths,
        planner: InitializePlanner | None = None,
        service: InitializeService | None = None,
        settings_loader: EnvSettingsLoader | None = None,
        proxy_renderer: RenderProxy | None = None,
        authoritative_renderer: RenderAuthoritative | None = None,
    ) -> None:
        self.paths = paths
        self.planner = planner or InitializePlanner()
        self.service = service or InitializeService()
        self.settings_loader = settings_loader or EnvSettingsLoader()
        self.proxy_renderer = proxy_renderer or RenderProxy(paths)
        self.authoritative_renderer = authoritative_renderer or RenderAuthoritative(paths)

    def execute(self, render_only: bool = False, dry_run: bool = False, apply_only: bool = False) -> None:
        self.service.assert_not_initialized(self.paths.setup_file)
        settings = self.settings_loader.load(self.paths.setup_file)
        role = settings.get("ROLE", "").strip()
        node = settings.get("NODE_NAME", "local").strip() or "local"

        if role == DnsRole.AUTHORITATIVE.value:
            if not apply_only:
                self.authoritative_renderer.execute(node)
            render_root = self.paths.render_dir(DnsRole.AUTHORITATIVE, node)
            plan = self.planner.build_authoritative_plan(node, render_root, dry_run, backup_before_apply=True)
        elif role == DnsRole.PROXY.value:
            proxy_type = ProxyType.from_value(settings.get("PROXY_TYPE", ProxyType.HYBRID.value))
            if not apply_only:
                self.proxy_renderer.execute(node, proxy_type)
            render_root = self.paths.render_dir(DnsRole.PROXY, node)
            plan = self.planner.build_proxy_plan(node, proxy_type.value, render_root, dry_run, backup_before_apply=True)
        else:
            raise SettingsError(f"unsupported ROLE in {self.paths.setup_file}: {role or '<missing>'}")

        print(plan.summary())
        if render_only:
            return

        self.service.apply(plan, setup_file=self.paths.setup_file)
