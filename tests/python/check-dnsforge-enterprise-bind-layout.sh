#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

PYTHONPATH="${PROJECT_ROOT}/src" python3 - <<'PY'
from pathlib import Path
import tempfile

from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.model.roles import DnsRole
from dnsforge.domain.model.settings import AuthoritativeSettings, ProxySettings
from dnsforge.infrastructure.bind.layout import BindLayoutDetector
from dnsforge.infrastructure.bind.permissions import BindPermissionPolicy
from dnsforge.infrastructure.rendering.bind_renderer import BindRenderTree

for family, named_conf, config_dir, data_dir in (
    ("redhat", "etc/named.conf", "etc/named", "var/named"),
    ("debian", "etc/bind/named.conf", "etc/bind", "var/lib/bind"),
    ("suse", "etc/named.conf", "etc/named", "var/lib/named"),
):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        layout = BindLayoutDetector().from_family(family)
        renderer = BindRenderTree(layout=layout)
        settings = AuthoritativeSettings(role=DnsRole.AUTHORITATIVE, node_name="ns1", raw={"SECURITY_PROFILE": "enterprise"})
        renderer.render_authoritative(settings, root)
        assert (root / named_conf).exists(), family
        assert (root / config_dir / "conf.d/00-acl.conf").exists(), family
        assert (root / config_dir / "conf.d/10-keys.conf").exists(), family
        assert (root / config_dir / "conf.d/20-options.conf").exists(), family
        assert (root / config_dir / "conf.d/30-logging.conf").exists(), family
        assert (root / config_dir / "conf.d/40-controls.conf").exists(), family
        assert (root / config_dir / "conf.d/45-statistics.conf").exists(), family
        assert (root / config_dir / "conf.d/60-views.conf").exists(), family
        assert (root / config_dir / "views/external/zones.available").is_dir(), family
        assert (root / config_dir / "views/external/zones.enabled/zones.index.conf").exists(), family
        assert (root / config_dir / "views/internal/templates/master.conf.tpl").exists(), family
        assert (root / config_dir / "tsig/rndc.key").exists(), family
        assert (root / config_dir / "catalog/catalog.zone").exists(), family
        assert (root / data_dir / "master/external").is_dir(), family
        assert (root / data_dir / "master/internal").is_dir(), family
        assert (root / data_dir / "secondary").is_dir(), family
        assert (root / data_dir / "dynamic/managed-keys.bind").exists(), family
        assert (root / data_dir / "rpz").is_dir(), family
        assert (root / data_dir / "data/named_stats.txt").exists(), family
        assert (root / "var/log/named/default.log").exists(), family
        named = (root / named_conf).read_text(encoding="utf-8")
        assert str(layout.config_dir / "conf.d/20-options.conf") in named
        assert "/etc/dnsforge/generated" not in named
        assert "/var/lib/dnsforge" not in named
        assert all(str(rule.path) for rule in BindPermissionPolicy(layout).rules())

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    layout = BindLayoutDetector().from_family("redhat")
    renderer = BindRenderTree(layout=layout)
    settings = ProxySettings(role=DnsRole.PROXY, node_name="proxy1", proxy_type=ProxyType.HYBRID, raw={"ENABLE_RPZ": "yes", "SECURITY_PROFILE": "enterprise"})
    renderer.render_proxy(settings, root)
    assert (root / "etc/named.conf").exists()
    assert (root / "etc/named/conf.d/50-rpz.conf").exists()
    assert (root / "etc/named/conf.d/60-views.conf").exists()
    assert (root / "var/named/rpz/rpz.local.zone").exists()
PY

echo "dnsforge enterprise native BIND layout validation OK"
