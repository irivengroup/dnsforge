from __future__ import annotations

import json
from pathlib import Path

from dnsforge.application.catalog.catalog_service import CatalogService
from dnsforge.application.cluster.cluster_service import ClusterService
from dnsforge.application.health.score_service import HealthScoreService
from dnsforge.application.security.security_service import SecurityService
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class ReportService:
    def __init__(self, paths: ProjectPaths) -> None:
        self.paths = paths

    def generate(self, *, output_format: str = "json", output: Path | None = None) -> str:
        data = {
            "health": HealthScoreService().score(self.paths.setup_file, self.paths.project_root),
            "catalog": CatalogService(self.paths).status(),
            "cluster": ClusterService().status(self.paths.setup_file),
            "security": SecurityService().show(self.paths.setup_file),
        }
        rendered = self._render(data, output_format)
        if output is not None:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered + "\n", encoding="utf-8")
        return rendered

    def _render(self, data: dict[str, object], output_format: str) -> str:
        if output_format == "json":
            return json.dumps(data, indent=2, sort_keys=True)
        if output_format == "yaml":
            lines: list[str] = []
            for key, value in data.items():
                lines.append(f"{key}:")
                for line in str(value).splitlines() or [""]:
                    lines.append(f"  {line}")
            return "\n".join(lines)
        if output_format == "html":
            body = "".join(f"<h2>{key}</h2><pre>{value}</pre>" for key, value in data.items())
            return f"<!doctype html><html><body><h1>DNSForge Report</h1>{body}</body></html>"
        raise ValueError(f"unsupported report format: {output_format}")
