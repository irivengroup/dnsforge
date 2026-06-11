from __future__ import annotations

import os
from pathlib import Path

from dnsforge.domain.model.roles import DnsRole
from dnsforge.infrastructure.bind.layout import BindLayout, BindLayoutDetector


class ProjectPaths:
    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path.cwd()

    @property
    def src_root(self) -> Path:
        return self.project_root / "src"

    @property
    def product_root(self) -> Path:
        return self.src_root / "dnsforge"

    @property
    def settings_root(self) -> Path:
        return Path(os.environ.get("DNSFORGE_CONFIG_ROOT", "/etc/dnsforge"))

    @property
    def infrastructure_root(self) -> Path:
        return self.product_root / "infrastructure"

    @property
    def template_root(self) -> Path:
        return self.infrastructure_root / "templates"

    @property
    def build_root(self) -> Path:
        # Backward-compatible property name. The physical build/ tree was removed;
        # template assets now live in infrastructure/bind/rendering.
        return self.template_root

    @property
    def catalog_file(self) -> Path:
        # DNSForge zone catalog is node configuration, not a BIND template asset.
        return Path(os.environ.get("DNSFORGE_ZONE_CATALOG", str(self.settings_root / "zones.yml")))

    @property
    def render_root(self) -> Path:
        # Render staging remains a temporary project build area. DNSForge runtime
        # configuration/data is deployed only to the native BIND layout.
        return self.src_root / "render"

    @property
    def bind_layout(self) -> BindLayout:
        return BindLayoutDetector().detect()

    @property
    def setup_file(self) -> Path:
        return Path(os.environ.get("DNSFORGE_SETUP_FILE", str(self.settings_root / "setup.conf")))

    def settings_file(self, role: DnsRole, node: str) -> Path:
        # setup.conf is the node source of truth. Legacy per-role files are kept
        # only as a fallback for old tests/migrations.
        if self.setup_file.exists():
            return self.setup_file
        if role is DnsRole.PROXY:
            return self.settings_root / "dns-proxy" / f"{node}.env"
        if role is DnsRole.AUTHORITATIVE:
            return self.settings_root / "dns-authoritative" / f"{node}.env"
        raise ValueError(role)

    def render_dir(self, role: DnsRole, node: str) -> Path:
        if role is DnsRole.PROXY:
            return self.render_root / "dns-proxy" / node
        if role is DnsRole.AUTHORITATIVE:
            return self.render_root / "dns-authoritative" / node
        raise ValueError(role)
