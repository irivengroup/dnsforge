from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_platform_support_gate_passes() -> None:
    completed = subprocess.run(
        [sys.executable, "tools/check_platform_support.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_platform_support_documents_minimum_versions() -> None:
    combined = "\n".join(
        (PROJECT_ROOT / rel).read_text(encoding="utf-8")
        for rel in (
            "docs/PLATFORM_SUPPORT.md",
            "docs/CERTIFICATION_MATRIX.md",
            "docs/CI_CERTIFICATION_POLICY.md",
        )
    )
    assert "RHEL / Rocky / Alma 8+" in combined
    assert "Ubuntu 22.04" in combined
    assert "Debian 10+" in combined
    assert "SUSE / SLES 12+" in combined
