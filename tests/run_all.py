#!/usr/bin/env python3
"""Run the active DNSForge Python test suite."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    return subprocess.call([sys.executable, "-m", "pytest", "tests"], cwd=PROJECT_ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
