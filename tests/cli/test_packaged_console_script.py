from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_console_entrypoint_module_help() -> None:
    project_root = Path(__file__).resolve().parents[2]
    src_path = project_root / "src"
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(src_path) if not existing else f"{src_path}{os.pathsep}{existing}"

    result = subprocess.run(
        [sys.executable, "-m", "dnsforge.interfaces.cli.main", "--help"],
        text=True,
        capture_output=True,
        check=True,
        env=env,
    )
    assert "dnsforge" in result.stdout.lower()
