from __future__ import annotations

import os
from pathlib import Path


def main() -> int:
    version = os.environ.get("PYTHON_VERSION", "unknown")
    lines = [
        "# DNSForge quality report",
        "",
        f"- Python: `{version}`",
        "- Ruff lint: blocking",
        "- Ruff format: blocking",
        "- Mypy: blocking",
        "- Pytest: blocking",
        "- Skips in CI: forbidden",
        "- Coverage gate: 60% minimum",
        "- BIND tools validation: blocking in CI",
        "- Bandit: blocking",
        "- pip-audit: blocking",
        "- Wheel build/install: blocking",
        "- Wheel artifact upload: enabled",
        "",
    ]
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write("\n".join(lines))
            handle.write("\n")
    else:
        print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
