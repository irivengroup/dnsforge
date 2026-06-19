from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_upgrade_certification_gate_passes() -> None:
    completed = subprocess.run(
        [sys.executable, "tools/check_upgrade_certification.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_upgrade_and_migration_docs_capture_enterprise_baseline() -> None:
    upgrade_doc = (PROJECT_ROOT / "docs" / "UPGRADE_CERTIFICATION.md").read_text(encoding="utf-8")
    migration_doc = (PROJECT_ROOT / "docs" / "MIGRATION_COMPATIBILITY.md").read_text(encoding="utf-8")
    combined = upgrade_doc + "\n" + migration_doc

    assert "11.x -> 12.x" in upgrade_doc
    assert "12.0.x -> 12.9.x" in upgrade_doc
    assert "proxy-forwarder -> proxy-hybrid" in migration_doc
    assert "proxy-hybrid -> proxy-forwarder" in migration_doc
    assert "RHEL / Rocky / Alma 8+" in combined
    assert "Ubuntu 22.04+" in combined
    assert "Debian 10+" in combined
    assert "SUSE / SLES 12+" in combined
