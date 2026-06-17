#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import stat
from collections.abc import Callable
from pathlib import Path
from typing import Any

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
    # Delete children before parents so nested caches never outlive their container.
    return sorted(artifacts, key=lambda item: (len(item.parts), str(item)), reverse=True)


def _make_writable(path: Path) -> None:
    """Best-effort chmod for read-only artifacts before deletion.

    This does not bypass ownership; CI must run this script with sudo when previous
    sudo test steps created root-owned caches.
    """
    try:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    except FileNotFoundError:
        return
    except PermissionError:
        return


def _on_rm_error(function: Callable[[str], Any], path: str, _exc_info: object) -> None:
    target = Path(path)
    _make_writable(target)
    function(path)


def clean(artifacts: list[Path]) -> None:
    for path in artifacts:
        if not path.exists() and not path.is_symlink():
            continue
        if path.is_dir() and not path.is_symlink():
            for child in path.rglob("*"):
                _make_writable(child)
            _make_writable(path)
            shutil.rmtree(path, onerror=_on_rm_error)
        else:
            _make_writable(path)
            path.unlink(missing_ok=True)


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
        if any(path.owner() == "root" for path in artifacts if path.exists()):
            print("Hint: root-owned artifacts detected; run: sudo python tools/clean.py --fix")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
