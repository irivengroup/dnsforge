from __future__ import annotations

from pathlib import Path

from dnsforge.infrastructure.bind.rendering import TemplateRegistry

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_template_registry_matches_resource_files() -> None:
    root = PROJECT_ROOT / "src/dnsforge/infrastructure/bind/resources"
    assert not (root / "templates").exists(), "infrastructure/bind/resources/templates is forbidden"
    assert not (PROJECT_ROOT / "src/dnsforge/infrastructure/build").exists(), "infrastructure/build is forbidden"
    actual = {p.relative_to(root) for p in root.rglob("*") if p.suffix in {".j2", ".tpl"}}
    registered = set(TemplateRegistry.templates())
    assert actual == registered
