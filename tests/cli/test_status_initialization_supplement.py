from __future__ import annotations

from pathlib import Path

from dnsforge.application.status.status_service import StatusService
from dnsforge.infrastructure.initialize.state_store import InitializeStateStore


def test_status_keeps_existing_output_and_adds_initialization_without_lock_path(tmp_path: Path) -> None:
    setup_file = tmp_path / "etc/dnsforge/setup.conf"
    setup_file.parent.mkdir(parents=True)
    setup_file.write_text(
        "ROLE=dns-authoritative\nENABLE_RPZ=true\nENABLE_DNSSEC=true\nENABLE_RRL=true\n",
        encoding="utf-8",
    )

    service = StatusService()
    output = service.show(setup_file)
    assert "Hostname:" in output
    assert "Role: dns-authoritative" in output
    assert "Initialization:" in output
    assert "Status: not initialized" in output
    assert ".initialized.conf.lock" not in output

    InitializeStateStore().mark_initialized(setup_file, role="authoritative", node="local")
    output = service.show(setup_file)
    assert "Status: initialized" in output
    assert "Initialized At:" in output
    assert "Role: authoritative" in output
    assert "Node: local" in output
    assert ".initialized.conf.lock" not in output
