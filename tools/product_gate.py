#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS = (
    ("CLI Coverage", [sys.executable, "tools/check_cli_coverage.py"]),
    ("API Coverage", [sys.executable, "tools/check_api_coverage.py"]),
    ("Event Coverage", [sys.executable, "tools/check_event_coverage.py"]),
    ("Service Coverage", [sys.executable, "tools/check_service_coverage.py"]),
    ("Release Hygiene", [sys.executable, "tools/release_check.py", "--skip-dist"]),
    ("Platform Support", [sys.executable, "tools/check_platform_support.py"]),
    ("Upgrade Certification", [sys.executable, "tools/check_upgrade_certification.py"]),
)


def main() -> int:
    failures: list[str] = []
    for name, command in CHECKS:
        result = subprocess.run(
            command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
        )
        if result.returncode == 0:
            print(f"{name:<24} 100%")
        else:
            print(f"{name:<24} FAILED")
            print(result.stdout.rstrip())
            failures.append(name)
    if failures:
        print("DNSForge Product Score .. FAILED")
        return 1
    print("DNSForge Product Score .. 100/100")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
