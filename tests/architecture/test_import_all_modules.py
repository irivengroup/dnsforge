from __future__ import annotations

import importlib
import pkgutil

import dnsforge


def test_all_dnsforge_modules_are_importable() -> None:
    failures: list[str] = []
    for module in pkgutil.walk_packages(dnsforge.__path__, prefix="dnsforge."):
        try:
            importlib.import_module(module.name)
        except Exception as exc:  # pragma: no cover - failure path prints details
            failures.append(f"{module.name}: {exc!r}")
    assert failures == []
