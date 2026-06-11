from __future__ import annotations

import shutil
from pathlib import Path

from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.model.settings import AuthoritativeSettings, ProxySettings
from dnsforge.domain.security.model import SecurityControls, SecurityProfile
from dnsforge.infrastructure.security.bind_security import BindSecurityOptionsRenderer
from dnsforge.domain.render.profile import ProxyRenderProfile


class BindConfigFactory:
    def __init__(self, security_renderer: BindSecurityOptionsRenderer | None = None) -> None:
        self.security_renderer = security_renderer or BindSecurityOptionsRenderer()

    def security_controls(self, settings: dict[str, str]) -> SecurityControls:
        return SecurityControls.from_profile(SecurityProfile.from_value(settings.get('SECURITY_PROFILE')))

    def named_conf(self, include_forwarders: bool, include_rpz: bool, include_local_zones: bool) -> str:
        includes = [
            'include "/etc/named/00-acl.conf";',
            'include "/etc/named/10-options.conf";',
            'include "/etc/named/20-logging.conf";',
            'include "/etc/named/30-rndc.conf";',
        ]

        if include_forwarders:
            includes.append('include "/etc/named/40-forwarders.conf";')

        if include_local_zones:
            includes.append('include "/etc/named/45-local-zones.conf";')
            includes.append('include "/etc/named/60-zone-routing.conf";')

        if include_rpz:
            includes.append('include "/etc/named/50-rpz.conf";')

        return "\n".join(includes) + "\n"

    def acl(self, settings: dict[str, str]) -> str:
        return "\n".join([
            'acl "recursive_clients" {',
            f'    {settings.get("BACK_RECURSIVE_CLIENTS", "localnets; localhost;")}',
            "};",
            "",
            'acl "admin_clients" {',
            f'    {settings.get("ADM_ALLOWED_CLIENTS", "localhost;")}',
            "};",
            "",
        ])

    def proxy_options(self, settings: dict[str, str]) -> str:
        return "\n".join([
            "options {",
            '    directory "/var/named";',
            "    recursion yes;",
            "    dnssec-validation auto;",
            "    listen-on port 53 { any; };",
            "    listen-on-v6 { none; };",
            self.security_renderer.render_options(self.security_controls(settings)),
            "};",
            self.security_renderer.render_rrl(self.security_controls(settings)),
            "",
        ])

    def authoritative_options(self, settings: dict[str, str]) -> str:
        return "\n".join([
            "options {",
            '    directory "/var/named";',
            "    recursion no;",
            "    dnssec-validation auto;",
            "    listen-on port 53 { any; };",
            "    listen-on-v6 { none; };",
            self.security_renderer.render_options(self.security_controls(settings)),
            "};",
            self.security_renderer.render_rrl(self.security_controls(settings)),
            "",
        ])

    def rndc(self, settings: dict[str, str]) -> str:
        key_name = settings.get("RNDC_KEY_NAME", "rndc-key")
        secret = settings.get("RNDC_SECRET", "")
        return "\n".join([
            f'key "{key_name}" {{',
            "    algorithm hmac-sha256;",
            f'    secret "{secret}";',
            "};",
            "",
            "controls {",
            f'    inet 127.0.0.1 port 953 allow {{ 127.0.0.1; }} keys {{ "{key_name}"; }};',
            "};",
            "",
        ])

    def forwarders(self, settings: dict[str, str]) -> str:
        return "\n".join([
            "forwarders {",
            f'    {settings.get("DNS_FORWARDERS", "8.8.8.8; 1.1.1.1;")}',
            "};",
            "",
        ])

    def rpz(self, settings: dict[str, str]) -> str:
        if settings.get("ENABLE_RPZ", "no") != "yes":
            return ""
        zone = settings.get("RPZ_ZONE_NAME", "rpz.local")
        return "\n".join([
            'response-policy {',
            f'    zone "{zone}";',
            "};",
            "",
        ])

    def logging(self) -> str:
        return 'logging { channel default_log { stderr; severity info; }; category default { default_log; }; };\n'


class BindRenderTree:
    def __init__(self, config_factory: BindConfigFactory | None = None) -> None:
        self.config_factory = config_factory or BindConfigFactory()

    def render_proxy(self, settings: ProxySettings, destination: Path) -> None:
        env = settings.to_env()
        profile = ProxyRenderProfile.from_proxy_type(settings.proxy_type)
        include_rpz = env.get("ENABLE_RPZ", "no") == "yes"

        self._reset(destination)
        self._common_tree(destination)

        self._write(destination / "etc/named.conf", self.config_factory.named_conf(True, include_rpz, profile.include_local_zones))
        self._write(destination / "etc/named/00-acl.conf", self.config_factory.acl(env))
        self._write(destination / "etc/named/10-options.conf", self.config_factory.proxy_options(env))
        self._write(destination / "etc/named/20-logging.conf", self.config_factory.logging())
        self._write(destination / "etc/named/30-rndc.conf", self.config_factory.rndc(env))
        self._write(destination / "etc/named/40-forwarders.conf", self.config_factory.forwarders(env))

        if include_rpz:
            self._write(destination / "etc/named/50-rpz.conf", self.config_factory.rpz(env))

        if profile.include_local_zones:
            self._write(destination / "etc/named/45-local-zones.conf", "// Hybrid proxy local zones.\n")
            self._write(destination / "etc/named/60-zone-routing.conf", "// Hybrid proxy zone routing.\n")
            (destination / "var/named/master").mkdir(parents=True, exist_ok=True)

    def render_authoritative(self, settings: AuthoritativeSettings, destination: Path) -> None:
        env = settings.to_env()
        self._reset(destination)
        self._common_tree(destination)

        self._write(destination / "etc/named.conf", self.config_factory.named_conf(False, False, False))
        self._write(destination / "etc/named/00-acl.conf", self.config_factory.acl(env))
        self._write(destination / "etc/named/10-options.conf", self.config_factory.authoritative_options(env))
        self._write(destination / "etc/named/20-logging.conf", self.config_factory.logging())
        self._write(destination / "etc/named/30-rndc.conf", self.config_factory.rndc(env))
        (destination / "var/named/master").mkdir(parents=True, exist_ok=True)

    def _common_tree(self, destination: Path) -> None:
        for rel in (
            "etc/named",
            "etc/sysconfig",
            "var/named/data",
            "var/named/dynamic",
            "var/named/rpz",
            "var/named/slaves",
            "usr/lib/systemd/system/named.service.d",
        ):
            (destination / rel).mkdir(parents=True, exist_ok=True)

        self._write(destination / "etc/sysconfig/named", 'OPTIONS="-4"\n')
        self._write(destination / "usr/lib/systemd/system/named.service.d/override.conf", "[Service]\nLimitNOFILE=65536\n")

    def _reset(self, destination: Path) -> None:
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True, exist_ok=True)

    def _write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
