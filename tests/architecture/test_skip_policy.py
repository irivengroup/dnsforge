from __future__ import annotations

from pathlib import Path


ALLOWED_SKIP_REASONS = (
    "BIND validation tools are not installed",
    "install scripts intentionally require root",
    "install maintenance scripts intentionally require root",
)


def test_pytest_skips_are_explicitly_approved() -> None:
    project_root = Path(__file__).resolve().parents[2]
    offenders: list[str] = []

    for path in sorted((project_root / "tests").rglob("test_*.py")):
        if path == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8")
        if "pytest.skip" not in text and "skipif" not in text and "mark.skip" not in text:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if "pytest.skip" in line or "skipif" in line or "mark.skip" in line:
                if not any(reason in line for reason in ALLOWED_SKIP_REASONS):
                    offenders.append(f"{path.relative_to(project_root)}:{line_number}: {line.strip()}")

    assert not offenders, "Unapproved pytest skip detected:\n" + "\n".join(offenders)
