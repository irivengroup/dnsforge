from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_PATHS = (
    "src/settings",
    "src/libs",
    "src/dnsforge/application/configure",
    "src/dnsforge/infrastructure/build",
    "src/dnsforge/infrastructure/templates",
    "src/dnsforge/infrastructure/bind/templates",
    "src/dnsforge/infrastructure/bind/templates/templates",
)


def test_forbidden_legacy_paths_are_absent() -> None:
    offenders = [path for rel in FORBIDDEN_PATHS if (path := PROJECT_ROOT / rel).exists()]
    assert offenders == []


def test_no_shell_files_in_product_or_tests() -> None:
    roots = (PROJECT_ROOT / "src", PROJECT_ROOT / "tests")
    offenders = []
    for root in roots:
        if root.exists():
            offenders.extend(str(path.relative_to(PROJECT_ROOT)) for path in root.rglob("*.sh"))
            offenders.extend(str(path.relative_to(PROJECT_ROOT)) for path in root.rglob("*.bash"))
    assert offenders == []
