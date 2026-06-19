#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = {
    "docs/ENTERPRISE_CI_VALIDATION.md": "enterprise validation policy",
    "tests/bind/test_generated_bind_config_validation.py": "real named-checkconf/named-checkzone validation",
    "tests/bind/test_live_named_smoke.py": "live named smoke validation",
    "tests/enterprise/test_manager_agent_integration.py": "Manager to DNSForge Agent integration",
    "tests/disaster/test_disaster_service.py": "disaster recovery service tests",
    "tests/catalog/test_catalog_service.py": "catalog zones service tests",
    "tests/security/test_dnssec_lifecycle.py": "DNSSEC lifecycle tests",
    "tests/manager/test_manager_security_agent_trust.py": "Manager security and trust tests",
}

CI_REQUIRED_SNIPPETS = {
    "bind9utils": "BIND check tools package",
    "bind9-dnsutils": "DNS query tools package",
    "bind9": "live named package",
    "tests/bind/test_generated_bind_config_validation.py": "explicit generated BIND validation",
    "tests/bind/test_live_named_smoke.py": "live named smoke test",
    "tools/check_enterprise_validation.py": "enterprise validation gate",
}

SECURITY_TEST_SNIPPETS = {
    "test_manager_security_agent_trust.py": (
        "approve_node",
        "rotate_node_token",
        "revoke_node",
        "viewer",
    ),
    "test_manager_agent_integration.py": (
        "RecordingDNSForgeNodeClient",
        "dry_run_change",
        "apply_change",
        "approved_plan_hash",
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_required_files() -> list[str]:
    errors: list[str] = []
    for relpath, description in REQUIRED_FILES.items():
        if not (ROOT / relpath).exists():
            errors.append(f"missing {description}: {relpath}")
    return errors


def check_ci_workflow() -> list[str]:
    workflow = ROOT / ".github" / "workflows" / "ci.yml"
    if not workflow.exists():
        return ["missing CI workflow: .github/workflows/ci.yml"]
    content = _read(workflow)
    return [
        f"CI does not include {description}: expected snippet {snippet!r}"
        for snippet, description in CI_REQUIRED_SNIPPETS.items()
        if snippet not in content
    ]


def check_security_test_content() -> list[str]:
    errors: list[str] = []
    for filename, snippets in SECURITY_TEST_SNIPPETS.items():
        matches = list((ROOT / "tests").rglob(filename))
        if not matches:
            errors.append(f"missing security/integration test file: {filename}")
            continue
        content = "\n".join(_read(path) for path in matches)
        for snippet in snippets:
            if snippet not in content:
                errors.append(f"{filename} does not exercise expected behavior: {snippet}")
    return errors


def run() -> int:
    errors: list[str] = []
    errors.extend(check_required_files())
    errors.extend(check_ci_workflow())
    errors.extend(check_security_test_content())
    if errors:
        print("DNSForge enterprise validation gate failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DNSForge enterprise validation gate passed")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "src"))
    raise SystemExit(run())
