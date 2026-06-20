#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "docs/RELEASE_VERIFICATION.md",
    "docs/MAINTENANCE_POLICY.md",
    "docs/GA_RELEASE_NOTES.md",
    "docs/PRODUCTION_GA_CHECKLIST.md",
    "docs/OPERATIONS_GUIDE.md",
    "docs/PLATFORM_SUPPORT.md",
    "docs/UPGRADE_CERTIFICATION.md",
    ".github/workflows/ci.yml",
    "tools/product_gate.py",
    "tools/check_ga_readiness.py",
    "tools/release_check.py",
    "tools/clean.py",
)

REQUIRED_CI_MARKERS = (
    "ruff format --check",
    "ruff check",
    "mypy src/dnsforge",
    "bandit -q -r src/dnsforge",
    "tools/product_gate.py",
    "tools/check_ga_readiness.py",
    "tools/release_check.py",
    "tools/clean.py --check-release",
    "twine check dist/*",
)


def _version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"$', text, re.MULTILINE)
    if not match:
        raise RuntimeError("pyproject.toml does not expose project.version")
    return match.group(1)


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).exists():
            errors.append(f"missing release verification dependency: {relative}")

    ci_path = ROOT / ".github/workflows/ci.yml"
    ci = ci_path.read_text(encoding="utf-8") if ci_path.exists() else ""
    for marker in REQUIRED_CI_MARKERS:
        if marker not in ci:
            errors.append(f"CI does not contain required verification marker: {marker}")

    version = _version()
    if version.startswith("13.") and not version.startswith("13.0."):
        errors.append(f"maintenance verification only applies to 13.0.x, got {version}")

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## {version}" not in changelog:
        errors.append(f"CHANGELOG.md does not contain an entry for {version}")

    if errors:
        print("DNSForge release verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("DNSForge release verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
