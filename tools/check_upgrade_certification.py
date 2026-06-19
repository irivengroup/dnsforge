#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = {
    "docs/UPGRADE_CERTIFICATION.md": (
        "11.x -> 12.x",
        "12.0.x -> 12.9.x",
        "disaster snapshot",
        "initialize lock",
        "setup.conf",
        "wheel",
        "sdist",
    ),
    "docs/MIGRATION_COMPATIBILITY.md": (
        "proxy-forwarder -> proxy-hybrid",
        "proxy-hybrid -> proxy-forwarder",
        "rollback",
        "snapshot",
        "setup.conf",
        "BIND configuration",
        "BIND data",
    ),
}

REQUIRED_TESTS = {
    "tests/cli/test_migration_render_deploy.py": (
        "proxy-forwarder",
        "proxy-hybrid",
        "rollback",
    ),
    "tests/disaster/test_disaster_service.py": (
        "snapshot",
        "restore",
    ),
    "tests/architecture/test_release_check.py": ("test_project_version_is_synchronized",),
}

CI_REQUIRED_SNIPPETS = (
    "tools/check_upgrade_certification.py",
    "tools/check_platform_support.py",
    "tools/check_enterprise_validation.py",
)

REQUIRED_PLATFORM_SNIPPETS = (
    "RHEL / Rocky / Alma 8+",
    "Ubuntu 22.04",
    "Debian 10+",
    "SUSE / SLES 12+",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_docs() -> list[str]:
    errors: list[str] = []
    for relpath, snippets in REQUIRED_DOCS.items():
        path = ROOT / relpath
        if not path.exists():
            errors.append(f"missing upgrade certification document: {relpath}")
            continue
        content = _read(path)
        for snippet in snippets:
            if snippet not in content:
                errors.append(f"{relpath} missing required snippet: {snippet!r}")
    return errors


def check_tests() -> list[str]:
    errors: list[str] = []
    for relpath, snippets in REQUIRED_TESTS.items():
        path = ROOT / relpath
        if not path.exists():
            errors.append(f"missing upgrade/migration certification test anchor: {relpath}")
            continue
        content = _read(path)
        for snippet in snippets:
            if snippet not in content:
                errors.append(f"{relpath} missing expected coverage anchor: {snippet!r}")
    return errors


def check_ci() -> list[str]:
    workflow = ROOT / ".github" / "workflows" / "ci.yml"
    if not workflow.exists():
        return ["missing CI workflow: .github/workflows/ci.yml"]
    content = _read(workflow)
    return [
        f"CI does not enforce upgrade certification gate: expected {snippet!r}"
        for snippet in CI_REQUIRED_SNIPPETS
        if snippet not in content
    ]


def check_platform_alignment() -> list[str]:
    docs = [ROOT / "docs" / "UPGRADE_CERTIFICATION.md", ROOT / "docs" / "MIGRATION_COMPATIBILITY.md"]
    combined = "\n".join(_read(path) for path in docs if path.exists())
    return [
        f"upgrade certification docs do not reference supported platform baseline: {snippet}"
        for snippet in REQUIRED_PLATFORM_SNIPPETS
        if snippet not in combined
    ]


def run() -> int:
    errors: list[str] = []
    errors.extend(check_docs())
    errors.extend(check_tests())
    errors.extend(check_ci())
    errors.extend(check_platform_alignment())
    if errors:
        print("DNSForge upgrade certification gate failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DNSForge upgrade certification gate passed")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "src"))
    raise SystemExit(run())
