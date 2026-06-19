from __future__ import annotations

import subprocess
import sys


def test_enterprise_validation_gate_passes() -> None:
    completed = subprocess.run(
        [sys.executable, "tools/check_enterprise_validation.py"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
