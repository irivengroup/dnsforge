#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r'^version = "([^"]+)"$', re.MULTILINE)
INIT_VERSION_RE = re.compile(r'^__version__ = "([^"]+)"$', re.MULTILINE)
FORBIDDEN_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
}
FORBIDDEN_SUFFIXES = (".pyc", ".pyo", ".pyd")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _pyproject_version() -> str:
    match = VERSION_RE.search(_read(ROOT / "pyproject.toml"))
    if not match:
        raise ValueError("pyproject.toml does not expose project.version")
    return match.group(1)


def _init_version() -> str:
    match = INIT_VERSION_RE.search(_read(ROOT / "src" / "dnsforge" / "__init__.py"))
    if not match:
        raise ValueError("src/dnsforge/__init__.py does not expose __version__")
    return match.group(1)


def _version_file() -> str:
    return _read(ROOT / "VERSION").strip()


def _dist_files() -> tuple[list[Path], list[Path]]:
    dist = ROOT / "dist"
    wheels = sorted(dist.glob("dnsforge-*.whl")) if dist.exists() else []
    sdists = sorted(dist.glob("dnsforge-*.tar.gz")) if dist.exists() else []
    return wheels, sdists


def _contains_forbidden_artifact(name: str) -> bool:
    path = Path(name)
    if any(part in FORBIDDEN_PARTS for part in path.parts):
        return True
    return path.suffix in FORBIDDEN_SUFFIXES


def _archive_members(path: Path) -> list[str]:
    if path.suffix == ".whl" or path.suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            return archive.namelist()
    if path.name.endswith(".tar.gz"):
        with tarfile.open(path, "r:gz") as archive:
            return archive.getnames()
    return []


def check_version_sync() -> list[str]:
    errors: list[str] = []
    versions = {
        "pyproject.toml": _pyproject_version(),
        "VERSION": _version_file(),
        "src/dnsforge/__init__.py": _init_version(),
    }
    expected = versions["pyproject.toml"]
    for source, version in versions.items():
        if version != expected:
            errors.append(f"version mismatch: {source}={version!r}, expected {expected!r}")
    return errors


def check_dist() -> list[str]:
    errors: list[str] = []
    version = _pyproject_version()
    wheels, sdists = _dist_files()
    expected_wheel_prefix = f"dnsforge-{version}-"
    expected_sdist_name = f"dnsforge-{version}.tar.gz"

    if len(wheels) != 1:
        errors.append(f"expected exactly one wheel in dist/, found {len(wheels)}")
    elif not wheels[0].name.startswith(expected_wheel_prefix):
        errors.append(f"wheel version mismatch: {wheels[0].name!r}, expected prefix {expected_wheel_prefix!r}")

    if len(sdists) != 1:
        errors.append(f"expected exactly one sdist in dist/, found {len(sdists)}")
    elif sdists[0].name != expected_sdist_name:
        errors.append(f"sdist version mismatch: {sdists[0].name!r}, expected {expected_sdist_name!r}")

    for artifact in [*wheels, *sdists]:
        for member in _archive_members(artifact):
            if _contains_forbidden_artifact(member):
                errors.append(f"forbidden generated artifact inside {artifact.name}: {member}")
                break
    return errors


def check_commands_doc() -> list[str]:
    from dnsforge.application.docs.commands_doc_service import CommandDocumentationService
    from dnsforge.interfaces.cli.application import DnsForgeArgumentParserFactory

    expected = CommandDocumentationService().generate(DnsForgeArgumentParserFactory().build())
    current_path = ROOT / "docs" / "COMMANDS.md"
    current = current_path.read_text(encoding="utf-8") if current_path.exists() else ""
    if current != expected:
        return [
            "docs/COMMANDS.md is not synchronized with the CLI parser; run: PYTHONPATH=src python tools/generate_commands_doc.py"
        ]
    return []


def run_checks(*, skip_dist: bool) -> int:
    errors: list[str] = []
    errors.extend(check_version_sync())
    errors.extend(check_commands_doc())
    if not skip_dist:
        errors.extend(check_dist())

    if errors:
        print("DNSForge release gate failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DNSForge release gate passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="DNSForge release consistency checker")
    parser.add_argument("--skip-dist", action="store_true", help="skip dist/ artifact checks")
    args = parser.parse_args()
    return run_checks(skip_dist=args.skip_dist)


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "src"))
    raise SystemExit(main())
