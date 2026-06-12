from __future__ import annotations

import subprocess
import sys


def test_console_entrypoint_module_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "dnsforge.interfaces.cli.main", "--help"],
        text=True,
        capture_output=True,
        check=True,
    )
    assert "dnsforge" in result.stdout.lower()
