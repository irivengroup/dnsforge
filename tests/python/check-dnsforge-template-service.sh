#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src"
cd "${PROJECT_ROOT}"
python3 - <<'PY'
from pathlib import Path
from dnsforge.infrastructure.bind.layout import BindLayoutDetector
from dnsforge.infrastructure.bind.rendering import TemplateRegistry, TemplateService

for family in ("redhat", "debian", "suse"):
    layout = BindLayoutDetector().from_family(family)
    svc = TemplateService(layout=layout)
    rendered = svc.render_text('include "/etc/named/conf.d/00-acl.conf";\nfile "/var/named/master/internal/example.zone";')
    assert str(layout.conf_d / "00-acl.conf") in rendered, rendered
    assert str(layout.master_view_data_dir("internal") / "example.zone") in rendered, rendered
    assert svc.destination_for("/etc/named/conf.d/20-options.conf") == layout.conf_d / "20-options.conf"
    assert svc.destination_for("/var/named/rpz/rpz.local.zone") == layout.rpz_data_dir / "rpz.local.zone"
    assert layout.named_conf in TemplateRegistry.destinations(layout)

root = Path("src/dnsforge/infrastructure/bind/resources")
assert not (root / "templates").exists()
actual = {p.relative_to(root) for p in root.rglob('*') if p.suffix in {'.j2', '.tpl'}}
assert actual == set(TemplateRegistry.templates()), actual
assert not Path("src/dnsforge/infrastructure/build").exists()
PY
