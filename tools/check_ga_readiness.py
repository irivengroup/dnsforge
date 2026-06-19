#!/usr/bin/env python3
from __future__ import annotations

import re
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _env() -> dict[str, str]:
    env = os.environ.copy()
    src = str(ROOT / "src")
    current = env.get("PYTHONPATH")
    env["PYTHONPATH"] = src if not current else f"{src}{os.pathsep}{current}"
    return env


CHECKS = (
    ("Operational Readiness", [sys.executable, "tools/check_operational_readiness.py"]),
    ("Platform Certification", [sys.executable, "tools/check_platform_support.py"]),
    ("Upgrade Certification", [sys.executable, "tools/check_upgrade_certification.py"]),
    ("Enterprise CI", [sys.executable, "tools/check_enterprise_validation.py"]),
    ("CLI/API Parity", [sys.executable, "tools/check_cli_api_parity.py"]),
    ("Documentation Parity", [sys.executable, "tools/check_documentation_parity.py"]),
    ("Dead Code Audit", [sys.executable, "tools/check_dead_code.py"]),
)


def _coverage_threshold() -> int:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r"^fail_under\s*=\s*(\d+)", text, re.MULTILINE)
    if not match:
        return 0
    return int(match.group(1))


def main() -> int:
    failures: list[str] = []
    if _coverage_threshold() < 90:
        failures.append("Coverage policy")
        print("Coverage policy       FAILED")
        print("coverage fail_under must be >= 90")
    else:
        print("Coverage policy       PASS")

    for name, command in CHECKS:
        result = subprocess.run(
            command, cwd=ROOT, env=_env(), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
        )
        if result.returncode == 0:
            print(f"{name:<22} PASS")
        else:
            print(f"{name:<22} FAILED")
            print(result.stdout.rstrip())
            failures.append(name)
    if failures:
        print("GA Readiness Gate     FAILED")
        return 1
    print("GA Readiness Gate     PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
