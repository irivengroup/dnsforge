from __future__ import annotations

import os
import tempfile
from pathlib import Path

from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.model.roles import DnsRole
from dnsforge.domain.model.settings import AuthoritativeSettings, ProxySettings
from dnsforge.infrastructure.rendering.bind_renderer import BindRenderTree


def test_proxy_enterprise_rendering_contains_security_directives() -> None:
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
            "qname-minimization relaxed;",
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


def test_authoritative_enterprise_rendering_disables_recursion() -> None:
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


def test_qname_minimization_boolean_settings_are_normalized_for_bind() -> None:
    os.environ["DNSFORGE_BIND_LAYOUT"] = "redhat"
    root = Path(tempfile.mkdtemp())
    settings = ProxySettings(
        role=DnsRole.PROXY,
        node_name="dnsforge-qname",
        raw={"ENABLE_RPZ": "yes", "DNS_QNAME_MINIMIZATION": "yes"},
        proxy_type=ProxyType.HYBRID,
    )
    BindRenderTree().render_proxy(settings, root)
    options = (root / "etc/named/conf.d/20-options.conf").read_text(encoding="utf-8")
    assert "qname-minimization relaxed;" in options
    assert "qname-minimization yes;" not in options

    root = Path(tempfile.mkdtemp())
    settings = ProxySettings(
        role=DnsRole.PROXY,
        node_name="dnsforge-qname-off",
        raw={"ENABLE_RPZ": "yes", "DNS_QNAME_MINIMIZATION": "no"},
        proxy_type=ProxyType.HYBRID,
    )
    BindRenderTree().render_proxy(settings, root)
    options = (root / "etc/named/conf.d/20-options.conf").read_text(encoding="utf-8")
    assert "qname-minimization disabled;" in options


def test_removed_bind_options_are_not_rendered() -> None:
    """Protect CI against BIND options removed from modern BIND releases."""
    removed_options = (
        "additional-from-cache",
        "dnssec-enable",
        "maintain-ixfr-base",
        "cleaning-interval",
    )
    for family in ("redhat", "debian", "suse"):
        for profile in ("authoritative", "proxy-hybrid"):
            os.environ["DNSFORGE_BIND_LAYOUT"] = family
            root = Path(tempfile.mkdtemp())
            if profile == "authoritative":
                settings = AuthoritativeSettings(
                    role=DnsRole.AUTHORITATIVE,
                    node_name="dnsforge-modern-bind",
                    raw={"SECURITY_PROFILE": "enterprise"},
                )
                BindRenderTree().render_authoritative(settings, root)
            else:
                settings = ProxySettings(
                    role=DnsRole.PROXY,
                    node_name="dnsforge-modern-bind",
                    raw={"ENABLE_RPZ": "yes", "SECURITY_PROFILE": "enterprise"},
                    proxy_type=ProxyType.HYBRID,
                )
                BindRenderTree().render_proxy(settings, root)
            rendered = "\n".join(path.read_text(encoding="utf-8") for path in root.rglob("*.conf"))
            for option in removed_options:
                assert option not in rendered, (family, profile, option)
