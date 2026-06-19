from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_operational_readiness_gate_passes() -> None:
    completed = subprocess.run(
        [sys.executable, "tools/check_operational_readiness.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_operational_documents_capture_production_baseline() -> None:
    docs = {
        name: (PROJECT_ROOT / "docs" / name).read_text(encoding="utf-8")
        for name in [
            "OPERATIONS_GUIDE.md",
            "RUNBOOKS.md",
            "GO_LIVE_CHECKLIST.md",
            "SECURITY_BASELINE.md",
        ]
    }

    assert "dnsforge readiness" in docs["OPERATIONS_GUIDE.md"]
    assert "DNSForge Manager" in docs["OPERATIONS_GUIDE.md"]
    assert "Disaster recovery" in docs["RUNBOOKS.md"]
    assert "DNSSEC rotation" in docs["RUNBOOKS.md"]
    assert "Backup tested" in docs["GO_LIVE_CHECKLIST.md"]
    assert "DNSSync dry-run" in docs["GO_LIVE_CHECKLIST.md"]
    assert "Firewall matrix" in docs["SECURITY_BASELINE.md"]
    assert "All DNSForge commands require root/sudo except `dnsforge version`" in docs["SECURITY_BASELINE.md"]
