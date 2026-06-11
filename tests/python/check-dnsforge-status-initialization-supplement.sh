#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from pathlib import Path
import tempfile

from dnsforge.application.status.status_service import StatusService
from dnsforge.infrastructure.initialize.state_store import InitializeStateStore

with tempfile.TemporaryDirectory() as tmp:
    setup_file = Path(tmp) / "etc/dnsforge/setup.conf"
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
PY

echo "dnsforge status initialization supplement validation OK"
