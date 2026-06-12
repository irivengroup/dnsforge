from __future__ import annotations

from pathlib import Path

from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.model.roles import DnsRole
from dnsforge.domain.model.settings import ProxySettings
from dnsforge.infrastructure.bind.layout import BindLayoutDetector
from dnsforge.infrastructure.rendering.bind_renderer import BindRenderTree


def test_zone_declarations_are_view_scoped_when_views_are_enabled(tmp_path: Path) -> None:
    layout = BindLayoutDetector().from_family("debian")
    settings = ProxySettings(
        role=DnsRole.PROXY,
        node_name="dnsforge-ci-proxy",
        raw={"ENABLE_RPZ": "yes", "SECURITY_PROFILE": "enterprise"},
        proxy_type=ProxyType.HYBRID,
    )

    BindRenderTree(layout=layout).render_proxy(settings, tmp_path)

    named_conf = (tmp_path / "etc/bind/named.conf").read_text(encoding="utf-8")
    views_conf = (tmp_path / "etc/bind/conf.d/60-views.conf").read_text(encoding="utf-8")

    assert 'include "/etc/bind/conf.d/60-views.conf";' in named_conf
    assert 'include "/etc/bind/conf.d/55-catalog.conf";' not in named_conf
    assert 'include "/etc/bind/conf.d/50-rpz.conf";' not in named_conf
    assert 'include "/etc/bind/conf.d/55-catalog.conf";' in views_conf
    assert 'include "/etc/bind/conf.d/50-rpz.conf";' in views_conf
    assert "response-policy {" in views_conf
