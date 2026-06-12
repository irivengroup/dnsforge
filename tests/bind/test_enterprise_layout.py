from __future__ import annotations

import tempfile
from pathlib import Path

from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.model.roles import DnsRole
from dnsforge.domain.model.settings import AuthoritativeSettings, ProxySettings
from dnsforge.infrastructure.bind.layout import BindLayoutDetector
from dnsforge.infrastructure.bind.permissions import BindPermissionPolicy
from dnsforge.infrastructure.rendering.bind_renderer import BindRenderTree


def test_enterprise_native_bind_layout_by_distribution() -> None:
    for family, named_conf, config_dir, data_dir in (
        ("redhat", "etc/named.conf", "etc/named", "var/named"),
        ("debian", "etc/bind/named.conf", "etc/bind", "var/lib/bind"),
        ("suse", "etc/named.conf", "etc/named", "var/lib/named"),
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            layout = BindLayoutDetector().from_family(family)
            renderer = BindRenderTree(layout=layout)
            settings = AuthoritativeSettings(
                role=DnsRole.AUTHORITATIVE,
                node_name="ns1",
                raw={"SECURITY_PROFILE": "enterprise"},
            )
            renderer.render_authoritative(settings, root)
            assert (root / named_conf).exists(), family
            for relative in (
                "conf.d/00-acl.conf",
                "conf.d/10-keys.conf",
                "conf.d/20-options.conf",
                "conf.d/30-logging.conf",
                "conf.d/40-controls.conf",
                "conf.d/45-statistics.conf",
                "conf.d/60-views.conf",
                "views/external/zones.enabled/zones.index.conf",
                "views/internal/templates/master.conf.tpl",
                "tsig/rndc.key",
                "catalog/catalog.zone",
            ):
                assert (root / config_dir / relative).exists(), (family, relative)
            assert (root / config_dir / "views/external/zones.available").is_dir(), family
            for relative in (
                "master/external",
                "master/internal",
                "secondary",
                "dynamic/managed-keys.bind",
                "rpz",
                "data/named_stats.txt",
            ):
                assert (root / data_dir / relative).exists(), (family, relative)
            assert (root / "var/log/named/default.log").exists(), family
            named = (root / named_conf).read_text(encoding="utf-8")
            assert str(layout.config_dir / "conf.d/20-options.conf") in named
            assert "/etc/dnsforge/generated" not in named
            assert "/var/lib/dnsforge" not in named
            assert all(str(rule.path) for rule in BindPermissionPolicy(layout).rules())


def test_proxy_hybrid_layout_contains_rpz() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        layout = BindLayoutDetector().from_family("redhat")
        renderer = BindRenderTree(layout=layout)
        settings = ProxySettings(
            role=DnsRole.PROXY,
            node_name="proxy1",
            proxy_type=ProxyType.HYBRID,
            raw={"ENABLE_RPZ": "yes", "SECURITY_PROFILE": "enterprise"},
        )
        renderer.render_proxy(settings, root)
        assert (root / "etc/named.conf").exists()
        assert (root / "etc/named/conf.d/50-rpz.conf").exists()
        assert (root / "etc/named/conf.d/60-views.conf").exists()
        assert (root / "var/named/rpz/rpz.local.zone").exists()
