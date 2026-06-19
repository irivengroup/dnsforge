from __future__ import annotations

from dnsforge.application.jobs.job_service import JobService
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


def test_job_service_bootstraps_and_records_dry_run(tmp_path, monkeypatch):
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(tmp_path / "etc"))
    service = JobService(ProjectPaths(tmp_path))

    listing = service.list()
    assert "cluster-audit" in listing
    assert "catalog-sync" in listing

    result = service.run("cluster-audit", dry_run=True)
    assert result.startswith("dry-run:")

    history = service.history()
    assert "cluster-audit" in history
    assert "dry-run" in history
