from __future__ import annotations

from pathlib import Path


def test_pep604_annotations_are_python39_safe() -> None:
    roots = [Path("src"), Path("tests")]
    offenders: list[str] = []
    for root in roots:
        for path in root.rglob("*.py"):
            source = path.read_text()
            if " | " in source or "|None" in source or "None|" in source:
                if not source.startswith("from __future__ import annotations"):
                    offenders.append(str(path))
    assert offenders == []
