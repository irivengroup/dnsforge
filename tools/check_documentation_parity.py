#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

from _cli_inventory import ROOT, iter_leaf_commands

COMMAND_RE = re.compile(r"^### `([^`]+)`$", re.MULTILINE)
REQUIRED_DOCS = {
    "README.md": ("DNSForge", "BIND", "dnsforge"),
    "docs/COMMANDS.md": ("Generated from the DNSForge CLI parser", "dnsforge readiness"),
    "docs/OPERATIONS_GUIDE.md": ("dnsforge readiness", "dnsforge validate"),
    "docs/RUNBOOKS.md": ("Rollback zone", "DNSSEC rotation"),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _documented_commands() -> set[str]:
    path = ROOT / "docs" / "COMMANDS.md"
    if not path.exists():
        return set()
    return set(COMMAND_RE.findall(_read(path)))


def check_command_parity() -> list[str]:
    exposed = set(iter_leaf_commands())
    documented = _documented_commands()
    errors: list[str] = []
    missing = sorted(exposed - documented)
    stale = sorted(documented - exposed)
    if missing:
        errors.append("commands exposed by parser but missing from docs/COMMANDS.md: " + ", ".join(missing))
    if stale:
        errors.append("commands documented but not exposed by parser: " + ", ".join(stale))
    return errors


def check_required_docs() -> list[str]:
    errors: list[str] = []
    for relpath, snippets in REQUIRED_DOCS.items():
        path = ROOT / relpath
        if not path.exists():
            errors.append(f"missing documentation file: {relpath}")
            continue
        content = _read(path)
        for snippet in snippets:
            if snippet not in content:
                errors.append(f"{relpath} missing required snippet: {snippet!r}")
    return errors


def main() -> int:
    errors = [*check_required_docs(), *check_command_parity()]
    if errors:
        print("DNSForge documentation parity failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Documentation Parity: PASS")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "src"))
    raise SystemExit(main())
