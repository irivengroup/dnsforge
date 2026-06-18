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

CACHE_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "htmlcov",
}
BUILD_DIR_NAMES = {
    "build",
    "dist",
}
FILE_NAMES = {".coverage", "coverage.xml"}
FILE_SUFFIXES = {".pyc", ".pyo", ".pyd"}


def is_cache_artifact(path: Path) -> bool:
    name = path.name
    if path.is_dir() and name in CACHE_DIR_NAMES:
        return True
    if path.is_file() and (name in FILE_NAMES or path.suffix in FILE_SUFFIXES):
        return True
    return False


def is_build_artifact(path: Path) -> bool:
    name = path.name
    if path.is_dir() and (name in BUILD_DIR_NAMES or name.endswith(".egg-info")):
        return True
    return False


def is_generated_artifact(path: Path, *, allow_dist: bool = False) -> bool:
    if allow_dist and path == REPO_ROOT / "dist":
        return False
    return is_cache_artifact(path) or is_build_artifact(path)


def iter_artifacts(root: Path, *, allow_dist: bool = False) -> list[Path]:
    artifacts: list[Path] = []
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        if is_generated_artifact(path, allow_dist=allow_dist):
            artifacts.append(path)
    return sorted(artifacts, key=lambda item: (len(item.parts), str(item)), reverse=True)


def _make_writable(path: Path) -> None:
    """Best-effort chmod for read-only artifacts before deletion.

    This does not bypass ownership; CI runs this script with sudo when previous
    sudo test steps created root-owned caches.
    """
    try:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    except (FileNotFoundError, PermissionError):
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


def _print_artifacts(artifacts: list[Path], *, allow_dist: bool) -> None:
    if allow_dist:
        print("Generated cache/build artifacts must not be shipped outside dist/:")
    else:
        print("Generated cache/build artifacts must not be committed or used as source input:")
    for path in artifacts:
        print(f"- {path.relative_to(REPO_ROOT)}")
    if any(path.exists() and _owned_by_root(path) for path in artifacts):
        print("Hint: root-owned artifacts detected; run: sudo python tools/clean.py --fix")


def _owned_by_root(path: Path) -> bool:
    try:
        return path.stat().st_uid == 0
    except FileNotFoundError:
        return False


def check_source() -> int:
    artifacts = iter_artifacts(REPO_ROOT, allow_dist=False)
    if artifacts:
        _print_artifacts(artifacts, allow_dist=False)
        return 1
    return 0


def check_release() -> int:
    artifacts = iter_artifacts(REPO_ROOT, allow_dist=True)
    if artifacts:
        _print_artifacts(artifacts, allow_dist=True)
        return 1

    dist = REPO_ROOT / "dist"
    wheels = sorted(dist.glob("dnsforge-*.whl")) if dist.exists() else []
    sdists = sorted(dist.glob("dnsforge-*.tar.gz")) if dist.exists() else []
    errors: list[str] = []
    if len(wheels) != 1:
        errors.append(f"expected exactly one DNSForge wheel in dist/, found {len(wheels)}")
    if len(sdists) != 1:
        errors.append(f"expected exactly one DNSForge source archive in dist/, found {len(sdists)}")
    if errors:
        print("Invalid release artifacts:")
        for error in errors:
            print(f"- {error}")
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="DNSForge repository hygiene checker")
    parser.add_argument("--check", action="store_true", help="alias for --check-source")
    parser.add_argument("--check-source", action="store_true", help="fail if cache/build artifacts are present")
    parser.add_argument(
        "--check-release",
        action="store_true",
        help="fail if cache/build artifacts are present outside dist/; require one wheel and one sdist",
    )
    parser.add_argument("--fix", action="store_true", help="remove cache/build artifacts, including dist/")
    parser.add_argument("--fix-release", action="store_true", help="remove cache/build artifacts but preserve dist/")
    args = parser.parse_args()

    selected = [args.check, args.check_source, args.check_release, args.fix, args.fix_release]
    if sum(bool(item) for item in selected) != 1:
        parser.error("use exactly one of --check, --check-source, --check-release, --fix or --fix-release")

    if args.fix:
        clean(iter_artifacts(REPO_ROOT, allow_dist=False))
        return 0
    if args.fix_release:
        clean(iter_artifacts(REPO_ROOT, allow_dist=True))
        return 0
    if args.check or args.check_source:
        return check_source()
    return check_release()


if __name__ == "__main__":
    raise SystemExit(main())
