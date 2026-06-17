#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "htmlcov",
    "build",
    "dist",
}
FILE_NAMES = {".coverage", "coverage.xml"}
FILE_SUFFIXES = {".pyc", ".pyo", ".pyd"}


def is_generated_artifact(path: Path) -> bool:
    name = path.name
    if path.is_dir() and (name in DIR_NAMES or name.endswith(".egg-info")):
        return True
    if path.is_file() and (name in FILE_NAMES or path.suffix in FILE_SUFFIXES):
        return True
    return False


def iter_artifacts(root: Path) -> list[Path]:
    artifacts: list[Path] = []
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        if is_generated_artifact(path):
            artifacts.append(path)
    # Delete parents before children when removing directories.
    return sorted(artifacts, key=lambda item: (len(item.parts), str(item)))


def clean(artifacts: list[Path]) -> None:
    for path in artifacts:
        if not path.exists():
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description="DNSForge repository hygiene checker")
    parser.add_argument("--check", action="store_true", help="fail if generated cache/build artifacts are present")
    parser.add_argument("--fix", action="store_true", help="remove generated cache/build artifacts")
    args = parser.parse_args()

    if not args.check and not args.fix:
        parser.error("use --check or --fix")

    artifacts = iter_artifacts(REPO_ROOT)
    if args.fix:
        clean(artifacts)
        return 0

    if artifacts:
        print("Generated artifacts must not be committed or shipped:")
        for path in artifacts:
            print(f"- {path.relative_to(REPO_ROOT)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
