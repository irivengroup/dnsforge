#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = {
    "docs/OPERATIONS_GUIDE.md": (
        "dnsforge readiness",
        "dnsforge initialize --render-only",
        "dnsforge validate",
        "DNSForge Manager",
        "DNSSync",
    ),
    "docs/RUNBOOKS.md": (
        "Create zone",
        "Rollback zone",
        "DNSSEC rotation",
        "Disaster recovery",
        "Migration",
    ),
    "docs/GO_LIVE_CHECKLIST.md": (
        "OS is certified",
        "dnsforge readiness",
        "Backup tested",
        "Restore tested",
        "DNSSync dry-run",
    ),
    "docs/SECURITY_BASELINE.md": (
        "SELinux",
        "AppArmor",
        "Firewall matrix",
        "TSIG",
        "RNDC",
        "DNSSEC",
    ),
}

REQUIRED_SOURCE_SNIPPETS = {
    "src/dnsforge/interfaces/cli/application.py": ("readiness", "ReadinessService"),
    "src/dnsforge/application/readiness/readiness_service.py": ("class ReadinessService",),
    "src/dnsforge/domain/readiness/readiness_report.py": ("class ReadinessReport",),
}

REQUIRED_TESTS = {
    "tests/readiness/test_readiness_cli.py": ("readiness",),
    "tests/readiness/test_readiness_service.py": ("ReadinessService",),
    "tests/operational/test_operational_readiness_gate.py": ("check_operational_readiness.py",),
}

CI_SNIPPETS = (
    "tools/check_operational_readiness.py",
    "tools/product_gate.py",
    "tools/release_check.py",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _check_required_files(mapping: dict[str, tuple[str, ...]], label: str) -> list[str]:
    errors: list[str] = []
    for relpath, snippets in mapping.items():
        path = ROOT / relpath
        if not path.exists():
            errors.append(f"missing {label}: {relpath}")
            continue
        content = _read(path)
        for snippet in snippets:
            if snippet not in content:
                errors.append(f"{relpath} missing required snippet: {snippet!r}")
    return errors


def check_ci() -> list[str]:
    workflow = ROOT / ".github" / "workflows" / "ci.yml"
    if not workflow.exists():
        return ["missing CI workflow: .github/workflows/ci.yml"]
    content = _read(workflow)
    return [
        f"CI does not enforce operational readiness gate: expected {snippet!r}"
        for snippet in CI_SNIPPETS
        if snippet not in content
    ]


def run() -> int:
    errors: list[str] = []
    errors.extend(_check_required_files(REQUIRED_DOCS, "operational document"))
    errors.extend(_check_required_files(REQUIRED_SOURCE_SNIPPETS, "readiness implementation anchor"))
    errors.extend(_check_required_files(REQUIRED_TESTS, "operational readiness test anchor"))
    errors.extend(check_ci())
    if errors:
        print("DNSForge operational readiness gate failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DNSForge operational readiness gate passed")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "src"))
    raise SystemExit(run())
