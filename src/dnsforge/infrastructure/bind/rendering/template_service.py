from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Mapping

from dnsforge.infrastructure.bind.layout import BindLayout, BindLayoutDetector


@dataclass(frozen=True)
class RenderedTemplate:
    """A rendered template payload and its native destination."""

    source: Path
    destination: Path
    content: str


class TemplateService:
    """Distribution-aware BIND template renderer.

    DNSForge uses Red Hat paths (/etc/named, /var/named, /run/named) as
    canonical internal references. The service adapts destinations and embedded
    include/file paths through the detected BindLayout without keeping an
    unused static template corpus in the repository.
    """

    def __init__(self, root: Path | None = None, layout: BindLayout | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[1] / "resources"
        self.layout = layout or BindLayoutDetector().detect()

    def template_path(self, *parts: str) -> Path:
        return self.root.joinpath(*parts)

    def render_file(self, relative_template: str | Path, variables: Mapping[str, object] | None = None) -> str:
        path = self.template_path(*Path(relative_template).parts)
        return self.render_text(path.read_text(encoding="utf-8"), variables)

    def render_text(self, template: str, variables: Mapping[str, object] | None = None) -> str:
        context = self._context(variables or {})
        rendered = self._render_jinja_like(template, context)
        rendered = Template(rendered).safe_substitute({k: str(v) for k, v in context.items()})
        return self.rewrite_bind_paths(rendered)

    def destination_for(self, redhat_native_path: str | Path) -> Path:
        """Convert a canonical Red Hat BIND path to the active OS layout path."""

        path = str(redhat_native_path)
        for old, new in self._path_replacements().items():
            if path == old:
                return Path(new)
            if path.startswith(old.rstrip("/") + "/"):
                return Path(new) / path[len(old.rstrip("/") + "/") :]
        return Path(path)

    def render_to_destination(
        self,
        relative_template: str | Path,
        redhat_destination: str | Path,
        variables: Mapping[str, object] | None = None,
    ) -> RenderedTemplate:
        source = self.template_path(*Path(relative_template).parts)
        return RenderedTemplate(
            source=source,
            destination=self.destination_for(redhat_destination),
            content=self.render_file(relative_template, variables),
        )

    def rewrite_bind_paths(self, content: str) -> str:
        """Rewrite embedded paths from canonical Red Hat layout to active layout."""

        rewritten = content
        # Longest first to avoid replacing /var/named before /var/named/data.
        for old, new in sorted(self._path_replacements().items(), key=lambda item: len(item[0]), reverse=True):
            rewritten = rewritten.replace(old, new)
        return rewritten

    def _context(self, variables: Mapping[str, object]) -> dict[str, object]:
        layout = self.layout
        context: dict[str, object] = {
            "NAMED_CONF": str(layout.named_conf),
            "BIND_CONFIG_DIR": str(layout.config_dir),
            "BIND_CONF_D": str(layout.conf_d),
            "BIND_VIEWS_DIR": str(layout.views_dir),
            "BIND_TSIG_DIR": str(layout.tsig_dir),
            "BIND_CATALOG_DIR": str(layout.catalog_conf_dir),
            "BIND_DATA_DIR": str(layout.data_dir),
            "BIND_MASTER_DIR": str(layout.master_data_dir),
            "BIND_SECONDARY_DIR": str(layout.secondary_data_dir),
            "BIND_DYNAMIC_DIR": str(layout.dynamic_data_dir),
            "BIND_RPZ_DIR": str(layout.rpz_data_dir),
            "BIND_STATS_DIR": str(layout.statistics_data_dir),
            "BIND_CACHE_DIR": str(layout.cache_dir),
            "BIND_LOG_DIR": str(layout.log_dir),
            "BIND_RUN_DIR": str(layout.run_dir),
            "BIND_SERVICE_NAME": layout.service_name,
        }
        context.update(variables)
        return context

    def _path_replacements(self) -> dict[str, str]:
        layout = self.layout
        return {
            "/etc/named.conf": str(layout.named_conf),
            "/etc/named": str(layout.config_dir),
            "/var/named/data": str(layout.statistics_data_dir),
            "/var/named/dynamic": str(layout.dynamic_data_dir),
            "/var/named/rpz": str(layout.rpz_data_dir),
            "/var/named/master": str(layout.master_data_dir),
            "/var/named/secondary": str(layout.secondary_data_dir),
            "/var/named": str(layout.data_dir),
            "/var/log/named": str(layout.log_dir),
            "/run/named": str(layout.run_dir),
            "/var/run/named": str(layout.run_dir),
        }

    def _render_jinja_like(self, template: str, context: Mapping[str, object]) -> str:
        # Minimal, deterministic renderer for the existing {{ VAR }} templates.
        def replace(match: re.Match[str]) -> str:
            key = match.group(1).strip()
            return str(context.get(key, match.group(0)))

        return re.sub(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*}}", replace, template)
