#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MINIMUM_PLATFORMS = {
    "RHEL / Rocky / Alma": "8+",
    "Ubuntu": "22.04",
    "Debian": "10+",
    "SUSE / SLES": "12+",
}

REQUIRED_DOCS = (
    "docs/PLATFORM_SUPPORT.md",
    "docs/CERTIFICATION_MATRIX.md",
    "docs/CI_CERTIFICATION_POLICY.md",
)

REQUIRED_SNIPPETS = (
    "RHEL / Rocky / Alma 8+",
    "Ubuntu 22.04",
    "Debian 10+",
    "SUSE / SLES 12+",
    "authoritative",
    "proxy-forwarder",
    "proxy-hybrid",
)

CI_SNIPPETS = (
    "tools/check_platform_support.py",
    "check_enterprise_validation.py",
    "test_generated_bind_config_validation.py",
    "test_live_named_smoke.py",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_docs_exist() -> list[str]:
    return [f"missing platform certification document: {rel}" for rel in REQUIRED_DOCS if not (ROOT / rel).exists()]


def check_policy_content() -> list[str]:
    combined = "\n".join(_read(ROOT / rel) for rel in REQUIRED_DOCS if (ROOT / rel).exists())
    errors: list[str] = []
    for family, minimum in MINIMUM_PLATFORMS.items():
        if family not in combined or minimum not in combined:
            errors.append(f"platform minimum not documented: {family} {minimum}")
    for snippet in REQUIRED_SNIPPETS:
        if snippet not in combined:
            errors.append(f"platform policy missing required snippet: {snippet}")
    return errors


def check_ci_gate() -> list[str]:
    workflow = ROOT / ".github" / "workflows" / "ci.yml"
    if not workflow.exists():
        return ["missing CI workflow: .github/workflows/ci.yml"]
    content = _read(workflow)
    return [
        f"CI does not enforce platform support gate: expected {snippet!r}"
        for snippet in CI_SNIPPETS
        if snippet not in content
    ]


def run() -> int:
    errors: list[str] = []
    errors.extend(check_docs_exist())
    errors.extend(check_policy_content())
    errors.extend(check_ci_gate())
    if errors:
        print("DNSForge platform support gate failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DNSForge platform support gate passed")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "src"))
    raise SystemExit(run())
