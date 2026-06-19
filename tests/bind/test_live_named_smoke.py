from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
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
    root, layout = helpers._render_profile("redhat", "authoritative")
    named_conf = root / layout.named_conf.relative_to("/")

    completed = subprocess.run(
        ["timeout", "3", named, "-g", "-c", str(named_conf), "-p", "1053"],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode in {0, 124}, "\n".join(
        [
            "named did not survive the live smoke startup window",
            "--- stdout ---",
            completed.stdout,
            "--- stderr ---",
            completed.stderr,
        ]
    )
