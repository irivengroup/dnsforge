from __future__ import annotations

import os
from pathlib import Path

from dnsforge.domain.model.roles import DnsRole


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
    def build_root(self) -> Path:
        return self.infrastructure_root / "build"

    @property
    def catalog_file(self) -> Path:
        return self.build_root / "catalog" / "zones.yml"

    @property
    def render_root(self) -> Path:
        return self.src_root / "render"

    def settings_file(self, role: DnsRole, node: str) -> Path:
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
