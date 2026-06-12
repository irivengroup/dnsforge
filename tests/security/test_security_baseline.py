from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_security_baseline_directives_exist_in_bind_resources() -> None:
    resource_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (PROJECT_ROOT / "src/dnsforge/infrastructure/bind/resources").rglob("*")
        if path.is_file()
    )
    for directive in (
        "allow-transfer",
        "allow-recursion",
        "allow-query-cache",
        "rate-limit",
        "minimal-responses",
        "dnssec-validation",
        "response-policy",
    ):
        assert directive in resource_text


def test_no_default_secret_placeholders_in_src_settings() -> None:
    settings = PROJECT_ROOT / "src/settings"
    if not settings.exists():
        return
    text = "\n".join(path.read_text(encoding="utf-8") for path in settings.rglob("*") if path.is_file())
    assert 'TSIG_SECRET="CHANGE_ME' not in text
    assert 'RNDC_SECRET="CHANGE_ME' not in text
