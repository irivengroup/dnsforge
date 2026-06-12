from __future__ import annotations

from pathlib import Path

from dnsforge.infrastructure.bind.rendering import TemplateRegistry

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_registered_templates_have_no_legacy_paths() -> None:
    root = PROJECT_ROOT / "src/dnsforge/infrastructure/bind/resources"
    for template in TemplateRegistry.templates():
        path = root / template
        assert path.exists(), f"missing registered template: {template}"
        content = path.read_text(encoding="utf-8")
        assert "/etc/dnsforge/generated" not in content
        assert "/var/lib/dnsforge" not in content
