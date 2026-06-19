#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

from _cli_inventory import ROOT, iter_leaf_commands

COMMAND_RE = re.compile(r"^### `([^`]+)`$", re.MULTILINE)


def main() -> int:
    commands = set(iter_leaf_commands())
    docs_path = ROOT / "docs" / "COMMANDS.md"
    documented = set(COMMAND_RE.findall(docs_path.read_text(encoding="utf-8"))) if docs_path.exists() else set()
    cli_tests = sorted((ROOT / "tests" / "cli").glob("test_*.py"))

    errors: list[str] = []
    missing_docs = sorted(commands - documented)
    stale_docs = sorted(documented - commands)
    if missing_docs:
        errors.append("commands missing from docs/COMMANDS.md: " + ", ".join(missing_docs))
    if stale_docs:
        errors.append("commands documented but not exposed by parser: " + ", ".join(stale_docs))
    if not cli_tests:
        errors.append("no CLI test files found under tests/cli")

    if errors:
        print("DNSForge CLI coverage failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"CLI Coverage: 100% ({len(commands)} commands documented; {len(cli_tests)} CLI test files present)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
