from __future__ import annotations

import os
from pathlib import Path

from dnsforge.application.deploy.deploy_service import DeployService
from dnsforge.application.render.render_authoritative import RenderAuthoritative
from dnsforge.application.render.render_proxy import RenderProxy
from dnsforge.application.validate.validate_authoritative import ValidateAuthoritative
from dnsforge.application.validate.validate_proxy import ValidateProxy
from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.model.roles import DnsRole
from dnsforge.infrastructure.config.history_repository import ConfigHistoryRepository
from dnsforge.infrastructure.filesystem.paths import ProjectPaths
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader
from dnsforge.shared.errors import SettingsError


class ConfigService:
    def __init__(
        self,
        paths: ProjectPaths,
        loader: EnvSettingsLoader | None = None,
        repository: ConfigHistoryRepository | None = None,
        proxy_renderer: RenderProxy | None = None,
        authoritative_renderer: RenderAuthoritative | None = None,
        deployer: DeployService | None = None,
    ) -> None:
        self.paths = paths
        self.loader = loader or EnvSettingsLoader()
        self.repository = repository or ConfigHistoryRepository(paths.backup_root / "config-history")
        self.proxy_renderer = proxy_renderer or RenderProxy(paths)
        self.authoritative_renderer = authoritative_renderer or RenderAuthoritative(paths)
        self.deployer = deployer or DeployService()

    def show(self) -> str:
        settings = self._settings()
        keys = [
            "ROLE",
            "PROXY_TYPE",
            "NODE_NAME",
            "DNSSEC_ENABLED",
            "RPZ_ENABLED",
            "CATALOG_ZONES_ENABLED",
            "CLUSTER_ENABLED",
            "VIEW_INTERNAL_ENABLED",
            "VIEW_EXTERNAL_ENABLED",
        ]
        lines = [f"Setup File: {self.paths.setup_file}"]
        for key in keys:
            lines.append(f"{key}: {settings.get(key, 'unset')}")
        return "\n".join(lines)

    def validate(self) -> str:
        role, node, proxy_type = self._resolved_profile()
        if role == DnsRole.PROXY.value:
            ValidateProxy(self.paths).execute(node, ProxyType.from_value(proxy_type or ProxyType.HYBRID.value))
        elif role == DnsRole.AUTHORITATIVE.value:
            ValidateAuthoritative(self.paths).execute(node)
        else:
            raise SettingsError(f"unsupported ROLE in {self.paths.setup_file}: {role or '<missing>'}")
        return "Configuration validation OK"

    def history(self) -> str:
        snapshots = self.repository.list()
        lines = ["ID\tTimestamp\tChecksum\tReason"]
        if not snapshots:
            lines.append("none")
        else:
            lines.extend(snapshot.title() for snapshot in snapshots)
        return "\n".join(lines)

    def diff(self, identifier: int | None = None, id1: int | None = None, id2: int | None = None) -> str:
        if id1 is not None or id2 is not None:
            if id1 is None or id2 is None:
                raise SettingsError("config diff requires both --id1 and --id2")
            return self.repository.diff(id1, id2)
        return self.repository.diff_current(self._setup_content(), identifier)

    def apply(self, reason: str, dry_run: bool = False) -> str:
        self._require_reason(reason)
        self.validate()
        snapshot = self.repository.create_snapshot(self._setup_content(), reason)
        role, node, proxy_type = self._resolved_profile()
        if role == DnsRole.PROXY.value:
            proxy = ProxyType.from_value(proxy_type or ProxyType.HYBRID.value)
            self.proxy_renderer.execute(node, proxy)
            render_root = self.paths.render_dir(DnsRole.PROXY, node)
        elif role == DnsRole.AUTHORITATIVE.value:
            self.authoritative_renderer.execute(node)
            render_root = self.paths.render_dir(DnsRole.AUTHORITATIVE, node)
        else:
            raise SettingsError(f"unsupported ROLE in {self.paths.setup_file}: {role or '<missing>'}")
        self.deployer.deploy(render_root, Path("/"), dry_run=dry_run)
        return f"Configuration applied: snapshot {snapshot.identifier}"

    def rollback(self, identifier: int, reason: str, dry_run: bool = False) -> str:
        self._require_reason(reason)
        current = self._setup_content()
        pre = self.repository.create_snapshot(current, f"pre-rollback-{identifier}: {reason}")
        snapshot = self.repository.get(identifier)
        if not dry_run:
            self.paths.setup_file.parent.mkdir(parents=True, exist_ok=True)
            self.paths.setup_file.write_text(snapshot.content, encoding="utf-8")
        if dry_run:
            return f"Configuration rollback dry-run OK: {identifier} (pre-snapshot {pre.identifier})"
        return self.apply(f"rollback-to-{identifier}: {reason}")

    def audit(self) -> tuple[bool, str]:
        settings = self._settings()
        findings: list[str] = []
        role = settings.get("ROLE", "")
        if role not in {DnsRole.AUTHORITATIVE.value, DnsRole.PROXY.value}:
            findings.append("ROLE is missing or unsupported")
        if (
            role == DnsRole.PROXY.value
            and settings.get("PROXY_TYPE", ProxyType.HYBRID.value) not in ProxyType.choices()
        ):
            findings.append("PROXY_TYPE is invalid")
        if not settings.get("NODE_NAME"):
            findings.append("NODE_NAME is missing")
        for key in ("DNSSEC_ENABLED", "RPZ_ENABLED", "CLUSTER_ENABLED"):
            if key in settings and settings[key].lower() not in {"yes", "no", "true", "false", "1", "0"}:
                findings.append(f"{key} must be boolean-like")
        if role == DnsRole.AUTHORITATIVE.value and settings.get("PROXY_TYPE"):
            findings.append("PROXY_TYPE must not be set for authoritative profile")
        if not findings:
            return True, "Configuration audit OK"
        return False, "\n".join(findings)

    def _settings(self) -> dict[str, str]:
        return self.loader.load(self.paths.setup_file)

    def _setup_content(self) -> str:
        if not self.paths.setup_file.exists():
            raise SettingsError(f"settings file not found: {self.paths.setup_file}")
        return self.paths.setup_file.read_text(encoding="utf-8")

    def _resolved_profile(self) -> tuple[str, str, str | None]:
        settings = self._settings()
        role = settings.get("ROLE", "").strip()
        node = settings.get("NODE_NAME", "local").strip() or "local"
        proxy_type = settings.get("PROXY_TYPE")
        return role, node, proxy_type

    def _require_reason(self, reason: str) -> None:
        if len((reason or "").strip()) < 8:
            raise SettingsError("--reason is required and must contain at least 8 characters")
