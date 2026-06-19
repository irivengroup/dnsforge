from __future__ import annotations

import json

from dnsforge.application.metrics.metrics_service import MetricsCollector
from dnsforge.application.sync.provider_service import SyncProviderService
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


def test_metrics_collector_exposes_operational_metrics(tmp_path, monkeypatch):
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(tmp_path / "etc"))

    output = MetricsCollector(ProjectPaths(tmp_path)).render_text()

    assert "catalog_members" in output
    assert "cluster_peers" in output


def test_sync_lists_providers():
    data = json.loads(SyncProviderService().providers_status())

    assert {item["provider"] for item in data} == {"cluster", "dnssync"}
