from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_performance_baseline_documents_ga_scenarios() -> None:
    content = (ROOT / "docs" / "PERFORMANCE_BASELINE.md").read_text(encoding="utf-8")
    for expected in (
        "dnsforge initialize --render-only",
        "dnsforge initialize --apply",
        "dnsforge validate",
        "dnsforge readiness",
        "dnsforge catalog sync",
        "100",
        "500",
        "1000",
    ):
        assert expected in content
