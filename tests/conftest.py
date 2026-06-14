"""Pytest bootstrap for DNSForge tests."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def pytest_sessionfinish(session, exitstatus):  # type: ignore[no-untyped-def]
    """Forbid hidden skips in CI while allowing local developer flexibility."""
    import os

    if os.environ.get("DNSFORGE_FORBID_SKIPS") != "1":
        return

    terminal = session.config.pluginmanager.get_plugin("terminalreporter")
    skipped = [] if terminal is None else terminal.stats.get("skipped", [])
    if skipped:
        count = len(skipped)
        session.exitstatus = 1
        if terminal is not None:
            terminal.write_sep("!", f"DNSForge CI forbids skipped tests: {count} skipped")
