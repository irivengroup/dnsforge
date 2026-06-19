from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_release_check(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "tools/release_check.py", *args],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_release_check_source_gate_passes() -> None:
    result = run_release_check("--skip-dist")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "release gate passed" in result.stdout


def test_project_version_is_synchronized() -> None:
    version = (PROJECT_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    init_content = (PROJECT_ROOT / "src" / "dnsforge" / "__init__.py").read_text(encoding="utf-8")
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert f'version = "{version}"' in pyproject
    assert f'__version__ = "{version}"' in init_content
