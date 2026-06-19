#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PATHS = (
    ROOT / "src" / "dnsforge" / "api",
    ROOT / "src" / "dnsforge" / "sync_foundation",
)
FORBIDDEN_IMPORTS = ("dnsforge.api", "dnsforge.sync_foundation")


def _python_files() -> list[Path]:
    return sorted((ROOT / "src").rglob("*.py")) + sorted((ROOT / "tests").rglob("*.py"))


def _import_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def main() -> int:
    errors: list[str] = []
    for path in FORBIDDEN_PATHS:
        if path.exists():
            errors.append(f"obsolete package still present: {path.relative_to(ROOT)}")
    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports = _import_names(tree)
        for forbidden in FORBIDDEN_IMPORTS:
            if forbidden in imports or any(name.startswith(forbidden + ".") for name in imports):
                errors.append(f"obsolete import {forbidden!r} found in {path.relative_to(ROOT)}")
    if errors:
        print("DNSForge dead-code audit failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Dead Code Audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
