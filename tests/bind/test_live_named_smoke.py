from __future__ import annotations

import importlib.util
import os
import re
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
    for path in [root, *root.rglob("*")]:
        if path.is_dir():
            # The live smoke test starts the host named package, which commonly
            # drops privileges before creating pid/session/managed-key files.
            # The relocated tree is disposable and removed at test teardown, so
            # make directories writable by the runtime user while keeping files
            # read-only for non-owners unless BIND explicitly rewrites them.
            path.chmod(
                stat.S_IRUSR
                | stat.S_IWUSR
                | stat.S_IXUSR
                | stat.S_IRGRP
                | stat.S_IWGRP
                | stat.S_IXGRP
                | stat.S_IROTH
                | stat.S_IWOTH
                | stat.S_IXOTH
            )
        elif path.is_file():
            path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)


def _isolate_named_runtime_for_smoke(root: Path, layout: Any) -> None:
    """Neutralize host runtime resources that make live named smoke flaky.

    The live smoke test validates that BIND can parse and start with the
    generated DNSForge views/zones/options. It must not compete with the host
    resolver for RNDC/statistics sockets, port 53, or production log paths.
    """
    config_dir = root / layout.config_dir.relative_to("/")
    controls = config_dir / "conf.d" / "40-controls.conf"
    if controls.exists():
        controls.write_text("// DNSForge CI live smoke: RNDC controls disabled.\n", encoding="utf-8")

    statistics = config_dir / "conf.d" / "45-statistics.conf"
    if statistics.exists():
        statistics.write_text("// DNSForge CI live smoke: statistics channel disabled.\n", encoding="utf-8")

    logging = config_dir / "conf.d" / "30-logging.conf"
    if logging.exists():
        logging.write_text(
            "// DNSForge CI live smoke: stderr-only logging.\n"
            "logging {\n"
            "    channel dnsforge_ci_stderr { stderr; severity info; };\n"
            "    category default { dnsforge_ci_stderr; };\n"
            "};\n",
            encoding="utf-8",
        )

    options = config_dir / "conf.d" / "20-options.conf"
    if options.exists():
        content = options.read_text(encoding="utf-8")
        # The command line -p flag does not override explicit listen-on port 53
        # statements. Use a non-privileged port so the smoke test cannot collide
        # with a host BIND/systemd-resolved listener.
        content = re.sub(r"listen-on\s+port\s+53", "listen-on port 1053", content)
        content = content.replace("listen-on-v6 port 53", "listen-on-v6 port 1053")
        options.write_text(content, encoding="utf-8")

    runtime_dirs = [
        root / layout.run_dir.relative_to("/"),
        root / layout.log_dir.relative_to("/"),
        root / layout.data_dir.relative_to("/") / "dynamic",
        root / layout.data_dir.relative_to("/") / "data",
        root / layout.cache_dir.relative_to("/"),
    ]
    for directory in runtime_dirs:
        directory.mkdir(parents=True, exist_ok=True)


def _require_named() -> str:
    named = shutil.which("named")
    if named:
        return named
    message = "BIND validation tools are not installed: named"
    if os.environ.get("GITHUB_ACTIONS", "").lower() == "true":
        raise AssertionError(message)
    pytest.skip("BIND validation tools are not installed: named")


def _detect_host_bind_family() -> str:
    """Detect the actual host BIND layout, ignoring test overrides.

    Other BIND tests deliberately set ``DNSFORGE_BIND_LAYOUT`` to validate all
    supported distributions. The live ``named`` smoke test is different: it
    starts the host package's ``named`` binary, so it must render and relocate
    the configuration for the real host layout, not for a leftover synthetic
    override such as ``redhat``.
    """
    from dnsforge.infrastructure.bind.layout import BindLayoutDetector

    original = os.environ.pop("DNSFORGE_BIND_LAYOUT", None)
    try:
        return BindLayoutDetector().detect().family
    finally:
        if original is not None:
            os.environ["DNSFORGE_BIND_LAYOUT"] = original


def test_named_starts_generated_authoritative_configuration_under_timeout() -> None:
    named = _require_named()
    helpers = _load_generated_bind_validation_module()

    host_family = _detect_host_bind_family()
    root, layout = helpers._render_profile(host_family, "authoritative")
    root = _relocate_generated_tree_to_bind_allowed_root(root, layout)
    _isolate_named_runtime_for_smoke(root, layout)
    _make_generated_tree_accessible_to_named(root)
    named_conf = root / layout.named_conf.relative_to("/")

    assert named_conf.exists(), f"generated named.conf not found after relocation: {named_conf}"
    assert not str(named_conf).startswith(
        "/tmp/"
    ), f"live named smoke test must not use /tmp because host confinement profiles may deny it: {named_conf}"

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
