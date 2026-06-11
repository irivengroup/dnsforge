#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${PROJECT_ROOT}"
PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
import os
import tempfile
from pathlib import Path

from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.model.roles import DnsRole
from dnsforge.domain.model.settings import AuthoritativeSettings, ProxySettings
from dnsforge.infrastructure.rendering.bind_renderer import BindRenderTree

for family in ("redhat", "debian", "suse"):
    os.environ["DNSFORGE_BIND_LAYOUT"] = family
    root = Path(tempfile.mkdtemp())
    settings = ProxySettings(
        role=DnsRole.PROXY,
        node_name="dnsforge-test",
        raw={"ENABLE_RPZ": "yes", "SECURITY_PROFILE": "enterprise"},
        proxy_type=ProxyType.HYBRID,
    )
    BindRenderTree().render_proxy(settings, root)
    rendered = "\n".join(path.read_text(encoding="utf-8") for path in root.rglob("*.conf"))
    for directive in (
        "minimal-responses yes;",
        "minimal-any yes;",
        "dnssec-validation auto;",
        "qname-minimization yes;",
        "response-policy",
        "rate-limit {",
        "max-cache-size",
        "fetches-per-server",
        "allow-query-cache",
        "allow-update { none; };",
        "blackhole { blackhole_clients; };",
        "statistics-channels",
    ):
        assert directive in rendered, (family, directive)
    assert "infrastructure/bind/rendering/templates" not in rendered

os.environ["DNSFORGE_BIND_LAYOUT"] = "redhat"
root = Path(tempfile.mkdtemp())
settings = AuthoritativeSettings(
    role=DnsRole.AUTHORITATIVE,
    node_name="dnsforge-auth",
    raw={"SECURITY_PROFILE": "enterprise"},
)
BindRenderTree().render_authoritative(settings, root)
options = (root / "etc/named/conf.d/20-options.conf").read_text(encoding="utf-8")
assert "recursion no;" in options
assert "allow-recursion { none; };" in options
assert "allow-query-cache { none; };" in options
assert "dnssec-validation auto;" in options
print("dnsforge enterprise bind rendering OK")
PY
