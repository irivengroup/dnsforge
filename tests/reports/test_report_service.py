from __future__ import annotations

import json

from dnsforge.application.reports.report_service import ReportService
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


def test_report_service_generates_json(tmp_path, monkeypatch):
    setup = tmp_path / "setup.conf"
    setup.write_text("ROLE=authoritative\nNODE_NAME=dns01\n", encoding="utf-8")
    monkeypatch.setenv("DNSFORGE_SETUP_FILE", str(setup))
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(tmp_path / "etc"))

    rendered = ReportService(ProjectPaths(tmp_path)).generate(output_format="json")
    data = json.loads(rendered)

    assert "health" in data
    assert "catalog" in data
    assert "cluster" in data
    assert "security" in data
