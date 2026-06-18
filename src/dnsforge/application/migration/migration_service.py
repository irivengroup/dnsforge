from __future__ import annotations

import datetime as dt
import re
import shutil
from pathlib import Path

from dnsforge.application.deploy.deploy_service import DeployService
from dnsforge.application.render.render_proxy import RenderProxy
from dnsforge.domain.migration.model import MigrationTarget
from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.model.roles import DnsRole
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader
from dnsforge.shared.errors import SettingsError


class MigrationService:
    """Migrate a proxy node between forwarder and hybrid modes.

    Migration is intentionally limited to proxy-forwarder <-> proxy-hybrid.
    It updates setup.conf, regenerates the complete BIND tree for the target
    mode, and deploys that tree so configuration files and zone data match the
    target DNSForge profile. It does not support authoritative <-> proxy role
    changes; those remain install-time decisions.
    """

    def __init__(
        self,
        paths: ProjectPaths | None = None,
        loader: EnvSettingsLoader | None = None,
        renderer: RenderProxy | None = None,
        deployer: DeployService | None = None,
    ) -> None:
        self.paths = paths or ProjectPaths()
        self.loader = loader or EnvSettingsLoader()
        self.renderer = renderer
        self.deployer = deployer or DeployService()

    def migrate(
        self,
        setup_file: Path,
        target: MigrationTarget,
        dry_run: bool = False,
        reason: str | None = None,
        target_root: Path = Path("/"),
    ) -> str:
        settings = self.loader.load(setup_file)
        role = settings.get("ROLE", "").strip("'\"")
        node = settings.get("NODE_NAME", "").strip("'\"") or "proxy"
        current_type = settings.get("PROXY_TYPE", "").strip("'\"")

        if role != "dns-proxy":
            raise SettingsError("only proxy-forwarder <-> proxy-hybrid migrations are supported")

        new_type = "forwarder" if target is MigrationTarget.PROXY_FORWARDER else "hybrid"
        if current_type == new_type:
            return f"Already on {target.value}"
        if current_type not in {"forwarder", "hybrid"}:
            raise SettingsError("current proxy type must be forwarder or hybrid")

        if not dry_run:
            self._require_reason(reason)

        plan = [
            f"proxy-{current_type} -> {target.value}",
            f"setup file: {setup_file}",
            f"render root: {self.paths.render_dir(DnsRole.PROXY, node)}",
            f"target root: {target_root}",
        ]
        if dry_run:
            return "Would migrate " + "; ".join(plan)

        backup = self._backup_setup(setup_file)
        original_text = setup_file.read_text(encoding="utf-8")
        try:
            setup_file.write_text(self._render_migrated_setup(original_text, new_type), encoding="utf-8")
            render_service = self.renderer or RenderProxy(self.paths)
            render_service.execute(node, ProxyType.from_value(new_type))
            render_root = self.paths.render_dir(DnsRole.PROXY, node)
            self.deployer.deploy(render_root, target_root=target_root, dry_run=False)
        except Exception:
            setup_file.write_text(original_text, encoding="utf-8")
            raise

        return (
            f"Migrated proxy-{current_type} -> {target.value}; "
            f"backup={backup}; rendered={self.paths.render_dir(DnsRole.PROXY, node)}; deployed={target_root}"
        )

    def _require_reason(self, reason: str | None) -> None:
        if len((reason or "").strip()) < 8:
            raise SettingsError("--reason is required and must contain at least 8 characters")

    def _backup_setup(self, setup_file: Path) -> Path:
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M%S")
        backup = setup_file.with_suffix(f".conf.backup.{stamp}")
        shutil.copy2(setup_file, backup)
        return backup

    def _render_migrated_setup(self, text: str, new_type: str) -> str:
        migrated = self._set_var(text, "ROLE", '"dns-proxy"')
        migrated = self._set_var(migrated, "PROXY_TYPE", f'"{new_type}"')
        local = "yes" if new_type == "hybrid" else "no"
        for key in ("ENABLE_PROXY_MASTER_ZONES", "ENABLE_PROXY_AUTHORITATIVE_ZONES", "ENABLE_PROXY_LOCAL_ZONES"):
            migrated = self._set_var(migrated, key, f'"{local}"')
        return migrated

    def _set_var(self, text: str, key: str, value: str) -> str:
        pattern = re.compile(rf"^\s*{key}=.*$", re.MULTILINE)
        line = f"{key}={value}"
        if pattern.search(text):
            return pattern.sub(line, text)
        return text.rstrip() + "\n" + line + "\n"
