from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CI_FILE = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"


def test_ci_runs_coverage_once_for_non_live_suite() -> None:
    ci = CI_FILE.read_text(encoding="utf-8")

    assert "Coverage gate for non-live test suite" in ci
    assert "--cov-fail-under=90" in ci
    assert "--ignore=tests/bind/test_live_named_smoke.py" in ci
    assert "--ignore=tests/bind/test_generated_bind_config_validation.py" in ci
    assert "Run pytest suite" not in ci


def test_ci_keeps_live_bind_smoke_isolated() -> None:
    ci = CI_FILE.read_text(encoding="utf-8")

    assert "Validate generated BIND configuration explicitly" in ci
    assert "tests/bind/test_generated_bind_config_validation.py" in ci
    assert "tests/bind/test_live_named_smoke.py" in ci


def test_product_gates_are_not_duplicated() -> None:
    ci = CI_FILE.read_text(encoding="utf-8")

    assert ci.count("tools/check_ga_readiness.py") == 1
    assert ci.count("tools/check_documentation_parity.py") == 1
    assert ci.count("tools/check_cli_api_parity.py") == 1
    assert ci.count("tools/check_dead_code.py") == 1
