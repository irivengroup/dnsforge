from __future__ import annotations

import json
from pathlib import Path

from dnsforge.application.health.health_service import HealthService
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


class HealthScoreService:
    def score(self, setup_file: Path, project_root: Path) -> dict[str, object]:
        report = HealthService().check(setup_file, project_root)
        base = 100 if report.ok else 70
        categories = {
            "dnssec": base,
            "catalog": base,
            "cluster": base,
            "rpz": base,
            "views": base,
        }
        return {
            "score": min(categories.values()),
            "categories": categories,
            "status": "PASS" if report.ok else "WARNING",
        }

    def render(self, paths: ProjectPaths, *, output_format: str = "text") -> str:
        data = self.score(paths.setup_file, paths.project_root)
        if output_format == "json":
            return json.dumps(data, indent=2, sort_keys=True)
        rows = [f"DNSForge Health Score: {data['score']}/100", ""]
        categories = data["categories"]
        if not isinstance(categories, dict):
            raise TypeError("health score categories must be a dictionary")
        for name, value in categories.items():
            rows.append(f"{name.upper():<12} {value}")
        return "\n".join(rows)
