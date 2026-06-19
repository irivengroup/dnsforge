from __future__ import annotations

from pathlib import Path

from dnsforge.application.disaster.disaster_service import DisasterRecoveryService
from dnsforge.infrastructure.bind.layout import BindLayoutDetector
from dnsforge.infrastructure.filesystem.paths import ProjectPaths


def test_disaster_snapshot_and_verify(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DNSFORGE_CONFIG_ROOT", str(tmp_path / "etc" / "dnsforge"))
    monkeypatch.setenv("DNSFORGE_BACKUP_ROOT", str(tmp_path / "backups"))
    paths = ProjectPaths(tmp_path)
    paths.setup_file.parent.mkdir(parents=True)
    paths.setup_file.write_text("ROLE=dns-authoritative\n", encoding="utf-8")
    service = DisasterRecoveryService(paths, layout=BindLayoutDetector().from_family("redhat"))

    result = service.snapshot("unit test change", target_root=tmp_path)
    snapshot = Path(result.split(": ", 1)[1])

    assert service.verify(snapshot) == "Disaster snapshot verification OK"
