from __future__ import annotations

import os
import tempfile
from pathlib import Path

from dnsforge.infrastructure.rendering.bind_renderer import BindRenderTree
from dnsforge.domain.model.roles import DnsRole
from dnsforge.domain.model.settings import AuthoritativeSettings, ProxySettings
from dnsforge.domain.model.proxy_type import ProxyType


def test_rendered_zone_templates_are_profile_and_scope_specific() -> None:
    os.environ["DNSFORGE_BIND_LAYOUT"] = "redhat"
    root = Path(tempfile.mkdtemp())
    settings = AuthoritativeSettings(role=DnsRole.AUTHORITATIVE, node_name="ns1", raw={"SECURITY_PROFILE": "enterprise"})
    BindRenderTree().render_authoritative(settings, root)

    internal_master = (root / "etc/named/views/internal/templates/master.conf.tpl").read_text(encoding="utf-8")
    external_master = (root / "etc/named/views/external/templates/master.conf.tpl").read_text(encoding="utf-8")
    assert "allow-query { recursive_clients; localhost; };" in internal_master
    assert "allow-query { any; };" in external_master
    assert "check-integrity yes;" in internal_master
    assert "check-integrity yes;" in external_master


def test_proxy_hybrid_keeps_forward_zone_templates() -> None:
    os.environ["DNSFORGE_BIND_LAYOUT"] = "redhat"
    root = Path(tempfile.mkdtemp())
    settings = ProxySettings(role=DnsRole.PROXY, node_name="px1", raw={"SECURITY_PROFILE": "enterprise"}, proxy_type=ProxyType.HYBRID)
    BindRenderTree().render_proxy(settings, root)

    forward_template = (root / "etc/named/views/internal/templates/forward.conf.tpl").read_text(encoding="utf-8")
    assert "type forward;" in forward_template
    assert "forward {{ FORWARD_POLICY }};" in forward_template
