from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run_tool(name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, f"tools/{name}"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def test_documentation_parity_gate_passes() -> None:
    completed = _run_tool("check_documentation_parity.py")
    assert completed.returncode == 0, completed.stdout
    assert "Documentation Parity: PASS" in completed.stdout


def test_cli_api_parity_gate_passes() -> None:
    completed = _run_tool("check_cli_api_parity.py")
    assert completed.returncode == 0, completed.stdout
    assert "CLI/API Parity: PASS" in completed.stdout


def test_dead_code_gate_passes() -> None:
    completed = _run_tool("check_dead_code.py")
    assert completed.returncode == 0, completed.stdout
    assert "Dead Code Audit: PASS" in completed.stdout


def test_ga_readiness_gate_exists_and_references_required_gates() -> None:
    content = (ROOT / "tools" / "check_ga_readiness.py").read_text(encoding="utf-8")
    for expected in (
        "Operational Readiness",
        "Platform Certification",
        "Upgrade Certification",
        "Enterprise CI",
        "CLI/API Parity",
        "Documentation Parity",
        "Dead Code Audit",
        "GA Readiness Gate",
    ):
        assert expected in content
