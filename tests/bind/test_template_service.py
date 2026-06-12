from __future__ import annotations

from pathlib import Path

from dnsforge.infrastructure.bind.layout import BindLayoutDetector
from dnsforge.infrastructure.bind.rendering import TemplateRegistry, TemplateService

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_template_service_rewrites_paths_by_distribution() -> None:
    for family in ("redhat", "debian", "suse"):
        layout = BindLayoutDetector().from_family(family)
        service = TemplateService(layout=layout)
        rendered = service.render_text(
            'include "/etc/named/conf.d/00-acl.conf";\nfile "/var/named/master/internal/example.zone";'
        )
        assert str(layout.conf_d / "00-acl.conf") in rendered
        assert str(layout.master_view_data_dir("internal") / "example.zone") in rendered
        assert service.destination_for("/etc/named/conf.d/20-options.conf") == layout.conf_d / "20-options.conf"
        assert service.destination_for("/var/named/rpz/rpz.local.zone") == layout.rpz_data_dir / "rpz.local.zone"
        assert layout.named_conf in TemplateRegistry.destinations(layout)


def test_template_registry_matches_resource_tree() -> None:
    root = PROJECT_ROOT / "src/dnsforge/infrastructure/bind/resources"
    assert not (root / "templates").exists()
    actual = {p.relative_to(root) for p in root.rglob("*") if p.suffix in {".j2", ".tpl"}}
    assert actual == set(TemplateRegistry.templates())
    assert not (PROJECT_ROOT / "src/dnsforge/infrastructure/build").exists()
