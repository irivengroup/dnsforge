from __future__ import annotations

import importlib.util
import os
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import pytest


def _load_generated_bind_validation_module() -> Any:
    path = Path(__file__).with_name("test_generated_bind_config_validation.py")
    spec = importlib.util.spec_from_file_location("dnsforge_generated_bind_validation", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load generated BIND validation helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _relocate_generated_tree_to_bind_allowed_root(root: Path, layout: Any) -> Path:
    """Move the generated tree below the rendered distro BIND config root.

    The live ``named`` smoke test must not assume Debian/Ubuntu paths.  The
    sandbox location is derived from the rendered ``BindLayout``: Debian/Ubuntu
    under ``/etc/bind``, RedHat/SUSE under ``/etc/named``.  This keeps the test
    aligned with DNSForge's distro-specific layout model while still avoiding
    ``/tmp`` paths that BIND confinement profiles commonly reject.
    """
    bind_root = Path(layout.config_dir)
    if not bind_root.is_dir() or not os.access(bind_root, os.W_OK):
        return root

    destination = Path(tempfile.mkdtemp(prefix="dnsforge-ci-", dir=bind_root))
    shutil.copytree(root, destination, dirs_exist_ok=True)

    # _render_profile rewrites native absolute paths to the original temporary
    # root so named-checkconf can validate without chroot. After relocating the
    # generated tree into /etc/bind for the live named smoke test, all rendered
    # include/file/directory references must point to the relocated root as well.
    # Otherwise named reads /etc/bind/.../etc/named.conf and immediately fails
    # on includes that still reference the old /tmp/dnsforge-* location.
    original_root = str(root)
    relocated_root = str(destination)
    for path in destination.rglob("*"):
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        rewritten = content.replace(original_root, relocated_root)
        if rewritten != content:
            path.write_text(rewritten, encoding="utf-8")

    shutil.rmtree(root)
    return destination


def _make_generated_tree_accessible_to_named(root: Path) -> None:
    """Allow named to traverse/read the generated tree during CI smoke tests.

    The test suite may run through sudo, and tempfile.mkdtemp creates the
    profile root with mode 0700. Ubuntu BIND may also drop privileges before
    loading the configuration. Keep generated files read-only for others, but
    make directories traversable and writable where BIND may create runtime
    files during startup.
    """
    writable_directory_names = {"run", "cache", "log", "logs", "dynamic"}
    for path in [root, *root.rglob("*")]:
        if path.is_dir():
            mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
            mode |= stat.S_IRGRP | stat.S_IXGRP
            mode |= stat.S_IROTH | stat.S_IXOTH
            if path.name in writable_directory_names:
                mode |= stat.S_IWGRP | stat.S_IWOTH
            path.chmod(mode)
        elif path.is_file():
            path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)


def _require_named() -> str:
    named = shutil.which("named")
    if named:
        return named
    message = "BIND validation tools are not installed: named"
    if os.environ.get("GITHUB_ACTIONS", "").lower() == "true":
        raise AssertionError(message)
    pytest.skip("BIND validation tools are not installed: named")


def test_named_starts_generated_authoritative_configuration_under_timeout() -> None:
    named = _require_named()
    helpers = _load_generated_bind_validation_module()
    from dnsforge.infrastructure.bind.layout import BindLayoutDetector

    host_family = BindLayoutDetector().detect().family
    root, layout = helpers._render_profile(host_family, "authoritative")
    root = _relocate_generated_tree_to_bind_allowed_root(root, layout)
    _make_generated_tree_accessible_to_named(root)
    named_conf = root / layout.named_conf.relative_to("/")

    try:
        completed = subprocess.run(
            ["timeout", "3", named, "-g", "-c", str(named_conf), "-p", "1053"],
            text=True,
            capture_output=True,
            check=False,
        )
    finally:
        shutil.rmtree(root, ignore_errors=True)

    assert completed.returncode in {0, 124}, "\n".join(
        [
            "named did not survive the live smoke startup window",
            "--- stdout ---",
            completed.stdout,
            "--- stderr ---",
            completed.stderr,
        ]
    )
