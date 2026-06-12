from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from dnsforge.domain.model.settings import AuthoritativeSettings, ProxySettings
from dnsforge.domain.render.profile import ProxyRenderProfile
from dnsforge.domain.security.model import SecurityControls, SecurityProfile
from dnsforge.domain.zone.model import ZoneType
from dnsforge.domain.zone.template_policy import ServerProfile, ZoneScope, ZoneTemplateKey, ZoneTemplatePolicy
from dnsforge.infrastructure.bind.layout import BindLayout, BindLayoutDetector
from dnsforge.infrastructure.security.bind_security import BindSecurityOptionsRenderer
from dnsforge.infrastructure.bind.rendering.template_service import TemplateService


@dataclass(frozen=True)
class BindConfiguration:
    """In-memory BIND configuration model produced by DNSForge.

    The factory owns the configuration decisions. Static templates only format
    this model into BIND files and must not contain distribution-specific hard
    coded destination logic.
    """

    layout: BindLayout
    settings: dict[str, str]
    include_rpz: bool
    include_views: bool
    proxy: bool


class BindConfigFactory:
    """Build the BIND configuration model and render model fragments.

    This is intentionally hybrid: DNSForge computes the complete BIND model in
    Python, then renders readable modular BIND files through TemplateService.
    """

    def __init__(
        self,
        security_renderer: BindSecurityOptionsRenderer | None = None,
        template_service: TemplateService | None = None,
    ) -> None:
        self.security_renderer = security_renderer or BindSecurityOptionsRenderer()
        self.template_service = template_service or TemplateService()

    def build_proxy_configuration(
        self, settings: dict[str, str], layout: BindLayout, include_views: bool
    ) -> BindConfiguration:
        return BindConfiguration(
            layout=layout,
            settings=settings,
            include_rpz=settings.get("ENABLE_RPZ", "no") == "yes",
            include_views=include_views,
            proxy=True,
        )

    def build_authoritative_configuration(self, settings: dict[str, str], layout: BindLayout) -> BindConfiguration:
        return BindConfiguration(layout=layout, settings=settings, include_rpz=False, include_views=True, proxy=False)

    def adapt(self, content: str) -> str:
        return self.template_service.rewrite_bind_paths(content)

    def security_controls(self, settings: dict[str, str]) -> SecurityControls:
        return SecurityControls.from_profile(SecurityProfile.from_value(settings.get("SECURITY_PROFILE")))

    def _render(self, template: str, variables: dict[str, object], layout: BindLayout) -> str:
        service = TemplateService(layout=layout)
        return service.render_file(template, variables)

    def named_conf(self, layout: BindLayout, include_rpz: bool, include_views: bool) -> str:
        includes = [
            layout.conf_d / "00-acl.conf",
            layout.conf_d / "10-keys.conf",
            layout.conf_d / "20-options.conf",
            layout.conf_d / "30-logging.conf",
            layout.conf_d / "40-controls.conf",
            layout.conf_d / "45-statistics.conf",
        ]
        # BIND requires every zone statement to live inside a view once any
        # view is declared. Catalog/RPZ zones are therefore included from
        # 60-views.conf for view-based profiles, not globally from named.conf.
        if include_views:
            includes.append(layout.conf_d / "60-views.conf")
        else:
            includes.append(layout.conf_d / "55-catalog.conf")
            if include_rpz:
                includes.append(layout.conf_d / "50-rpz.conf")
        include_block = "\n".join(f'include "{path}";' for path in includes)
        return self._render("named.conf.j2", {"INCLUDES": include_block}, layout)

    def acl(self, settings: dict[str, str], layout: BindLayout | None = None) -> str:
        layout = layout or self.template_service.layout
        return self._render(
            "00-acl.conf.j2",
            {
                "RECURSIVE_CLIENTS": settings.get("BACK_RECURSIVE_CLIENTS", "localnets; localhost;"),
                "ADMIN_CLIENTS": settings.get("ADM_ALLOWED_CLIENTS", "localhost;"),
                "ZONE_TRANSFER_CLIENTS": settings.get("XFR_ALLOWED_CLIENTS", "none;"),
                "BLACKHOLE_CLIENTS": settings.get("DNS_BLACKHOLE_CLIENTS", "none;"),
                "MONITORING_CLIENTS": settings.get("DNS_MONITORING_CLIENTS", "localhost;"),
            },
            layout,
        )

    @staticmethod
    def _qname_minimization_value(value: str | None) -> str:
        """Return a BIND-valid qname-minimization mode.

        BIND expects a mode such as ``relaxed``/``strict``/``disabled`` here,
        not a boolean. DNSForge still accepts legacy yes/no-style setup values
        and normalizes them before rendering the options block.
        """
        normalized = (value or "relaxed").strip().strip("\"'").lower()
        aliases = {
            "yes": "relaxed",
            "true": "relaxed",
            "1": "relaxed",
            "on": "relaxed",
            "enabled": "relaxed",
            "no": "disabled",
            "false": "disabled",
            "0": "disabled",
            "off": "disabled",
            "disable": "disabled",
            "disabled": "disabled",
            "relaxed": "relaxed",
            "strict": "strict",
        }
        return aliases.get(normalized, "relaxed")

    def _options(self, settings: dict[str, str], layout: BindLayout, proxy: bool) -> str:
        controls = self.security_controls(settings)
        recursion_acl = "recursive_clients; localhost;" if proxy else "none;"
        return self._render(
            "20-options.conf.j2",
            {
                "DATA_DIR": layout.data_dir,
                "DYNAMIC_DIR": layout.dynamic_data_dir,
                "PID_FILE": layout.run_dir / "named.pid",
                "SESSION_KEY_FILE": layout.run_dir / "session.key",
                "DUMP_FILE": layout.statistics_data_dir / "named_dump.db",
                "STATISTICS_FILE": layout.statistics_data_dir / "named_stats.txt",
                "MEMSTATISTICS_FILE": layout.statistics_data_dir / "named.memstats",
                "LISTEN_ON": settings.get("DNS_LISTEN_ON", "any;"),
                "LISTEN_ON_V6": settings.get("DNS_LISTEN_ON_V6", "none;"),
                "RECURSION": "yes" if proxy else "no",
                "ALLOW_RECURSION": recursion_acl,
                "ALLOW_QUERY_CACHE": recursion_acl,
                "ALLOW_QUERY": settings.get("DNS_ALLOW_QUERY", "any;"),
                "ALLOW_TRANSFER": settings.get("XFR_ALLOWED_CLIENTS", "zone_transfer_clients;"),
                "RPZ_RESPONSE_POLICY": "",
                "TCP_CLIENTS": settings.get("DNS_TCP_CLIENTS", "1000"),
                "RECURSIVE_CLIENTS_LIMIT": settings.get("DNS_RECURSIVE_CLIENTS_LIMIT", "10000" if proxy else "1000"),
                "CLIENTS_PER_QUERY": settings.get("DNS_CLIENTS_PER_QUERY", "10"),
                "MAX_CLIENTS_PER_QUERY": settings.get("DNS_MAX_CLIENTS_PER_QUERY", "100"),
                "MAX_CACHE_SIZE": settings.get("DNS_MAX_CACHE_SIZE", "512M" if proxy else "128M"),
                "MAX_CACHE_TTL": settings.get("DNS_MAX_CACHE_TTL", "86400"),
                "MAX_NCACHE_TTL": settings.get("DNS_MAX_NCACHE_TTL", "3600"),
                "MAX_RECURSION_DEPTH": settings.get("DNS_MAX_RECURSION_DEPTH", "7"),
                "MAX_RECURSION_QUERIES": settings.get("DNS_MAX_RECURSION_QUERIES", "100"),
                "FETCHES_PER_SERVER": settings.get("DNS_FETCHES_PER_SERVER", "100"),
                "FETCHES_PER_ZONE": settings.get("DNS_FETCHES_PER_ZONE", "500"),
                "QNAME_MINIMIZATION": self._qname_minimization_value(settings.get("DNS_QNAME_MINIMIZATION")),
                "SERVE_STALE": settings.get("DNS_SERVE_STALE", "yes" if proxy else "no"),
                "STALE_ANSWER_TTL": settings.get("DNS_STALE_ANSWER_TTL", "30"),
                "SECURITY_OPTIONS": self.security_renderer.render_options(controls),
                "RRL_OPTIONS": self.security_renderer.render_rrl(controls),
                "FORWARDERS_BLOCK": self.forwarders(settings) if proxy else "",
            },
            layout,
        )

    def proxy_options(self, settings: dict[str, str], layout: BindLayout) -> str:
        return self._options(settings, layout, proxy=True)

    def authoritative_options(self, settings: dict[str, str], layout: BindLayout) -> str:
        return self._options(settings, layout, proxy=False)

    def keys(self, settings: dict[str, str], layout: BindLayout | None = None) -> str:
        layout = layout or self.template_service.layout
        key_name = settings.get("RNDC_KEY_NAME", "rndc-key")
        secret = settings.get("RNDC_SECRET", "")
        blocks = [
            "\n".join(
                [
                    f'key "{key_name}" {{',
                    "    algorithm hmac-sha256;",
                    f'    secret "{secret}";',
                    "};",
                ]
            )
        ]
        xfr_key = settings.get("XFR_TSIG_KEY_NAME")
        xfr_secret = settings.get("XFR_TSIG_SECRET")
        if xfr_key and xfr_secret:
            blocks.append(
                "\n".join(
                    [
                        f'key "{xfr_key}" {{',
                        "    algorithm hmac-sha256;",
                        f'    secret "{xfr_secret}";',
                        "};",
                    ]
                )
            )
        return self._render("10-keys.conf.j2", {"KEY_BLOCKS": "\n\n".join(blocks)}, layout)

    def controls(self, settings: dict[str, str], layout: BindLayout | None = None) -> str:
        layout = layout or self.template_service.layout
        return self._render("40-controls.conf.j2", {"RNDC_KEY_NAME": settings.get("RNDC_KEY_NAME", "rndc-key")}, layout)

    def forwarders(self, settings: dict[str, str]) -> str:
        policy = settings.get("DNS_FORWARD_POLICY", "first")
        servers = settings.get("DNS_FORWARDERS", "8.8.8.8; 1.1.1.1;")
        return "\n".join([f"    forward {policy};", "    forwarders {", f"        {servers}", "    };", ""])

    def rpz_response_policy(self, settings: dict[str, str]) -> str:
        zone = settings.get("RPZ_ZONE_NAME", "rpz.local")
        return "\n".join(
            [
                "    response-policy {",
                f'        zone "{zone}" policy given;',
                "    } break-dnssec yes max-policy-ttl 300;",
            ]
        )

    def rpz(self, settings: dict[str, str]) -> str:
        return self.rpz_with_layout(settings, self.template_service.layout)

    def rpz_with_layout(self, settings: dict[str, str], layout: BindLayout) -> str:
        if settings.get("ENABLE_RPZ", "no") != "yes":
            return ""
        zone = settings.get("RPZ_ZONE_NAME", "rpz.local")
        block = "\n".join(
            [
                f'zone "{zone}" {{',
                "    type master;",
                f'    file "{layout.rpz_data_dir / "rpz.local.zone"}";',
                "    allow-query { localhost; admin_clients; };",
                "    allow-transfer { none; };",
                "    allow-update { none; };",
                "    notify no;",
                "};",
                "",
            ]
        )
        return self._render("50-rpz.conf.j2", {"RPZ_BLOCK": block}, layout)

    def logging(self, layout: BindLayout) -> str:
        return self._render("30-logging.conf.j2", {"LOG_DIR": layout.log_dir}, layout)

    def statistics(self, layout: BindLayout | None = None) -> str:
        layout = layout or self.template_service.layout
        return self._render("45-statistics.conf.j2", {"STATISTICS_PORT": "8053"}, layout)

    def views(self, layout: BindLayout, include_rpz: bool = False) -> str:
        return self._render(
            "60-views.conf.j2",
            {
                "INTERNAL_ZONE_INDEX": layout.zones_enabled_dir("internal") / "zones.index.conf",
                "EXTERNAL_ZONE_INDEX": layout.zones_enabled_dir("external") / "zones.index.conf",
                "INTERNAL_CATALOG_INCLUDE": f'    include "{layout.conf_d / "55-catalog.conf"}";',
                "INTERNAL_RPZ_INCLUDE": f'    include "{layout.conf_d / "50-rpz.conf"}";' if include_rpz else "",
                "INTERNAL_RPZ_RESPONSE_POLICY": self.rpz_response_policy({}) if include_rpz else "",
            },
            layout,
        )

    def zone_index(self, layout: BindLayout, view: str) -> str:
        return f"// DNSForge managed index for {view} view.\n"

    def zone_template(self, layout: BindLayout, profile: ServerProfile, scope: ZoneScope, zone_type: ZoneType) -> str:
        template = ZoneTemplatePolicy.template_path(ZoneTemplateKey(profile, scope, zone_type))
        zone_file = (
            layout.master_view_data_dir(scope.value) if zone_type is ZoneType.MASTER else layout.secondary_data_dir
        ) / "{{ zone_file }}"
        return self._render(
            str(template),
            {
                "ZONE_FILE": zone_file,
                "ALSO_NOTIFY": "{{ ALSO_NOTIFY }}",
                "MASTERS": "{{ MASTERS }}",
                "FORWARDERS": "{{ FORWARDERS }}",
                "FORWARD_POLICY": "{{ FORWARD_POLICY }}",
            },
            layout,
        )

    def master_template(self, layout: BindLayout, view: str) -> str:
        return self.zone_template(layout, ServerProfile.AUTHORITATIVE, ZoneScope.from_value(view), ZoneType.MASTER)

    def secondary_template(self, layout: BindLayout) -> str:
        return self.zone_template(layout, ServerProfile.AUTHORITATIVE, ZoneScope.INTERNAL, ZoneType.SECONDARY)

    def forward_template(self, layout: BindLayout | None = None) -> str:
        layout = layout or self.template_service.layout
        return self.zone_template(layout, ServerProfile.PROXY_FORWARDER, ZoneScope.INTERNAL, ZoneType.FORWARD)

    def catalog_conf(self, layout: BindLayout | None = None) -> str:
        layout = layout or self.template_service.layout
        return self._render(
            "55-catalog.conf.j2",
            {"CATALOG_ZONE_NAME": "catalog.dnsforge", "CATALOG_ZONE_FILE": layout.catalog_zone_file},
            layout,
        )

    def catalog_zone(self, layout: BindLayout | None = None) -> str:
        layout = layout or self.template_service.layout
        return self._render("catalog.zone.j2", {}, layout)

    def rpz_local_zone(self, layout: BindLayout | None = None) -> str:
        layout = layout or self.template_service.layout
        return self._render("rpz.local.zone.j2", {}, layout)


class BindRenderTree:
    def __init__(self, config_factory: BindConfigFactory | None = None, layout: BindLayout | None = None) -> None:
        self.layout = layout or BindLayoutDetector().detect()
        self.config_factory = config_factory or BindConfigFactory(template_service=TemplateService(layout=self.layout))

    def render_proxy(self, settings: ProxySettings, destination: Path) -> None:
        env = settings.to_env()
        profile = ProxyRenderProfile.from_proxy_type(settings.proxy_type)
        model = self.config_factory.build_proxy_configuration(env, self.layout, profile.include_local_zones)
        self._render_model(model, destination)

    def render_authoritative(self, settings: AuthoritativeSettings, destination: Path) -> None:
        model = self.config_factory.build_authoritative_configuration(settings.to_env(), self.layout)
        self._render_model(model, destination)

    def _render_model(self, model: BindConfiguration, destination: Path) -> None:
        self._reset(destination)
        self._common_tree(destination)

        layout = model.layout
        env = model.settings
        self._write_native(
            destination,
            layout.named_conf,
            self.config_factory.named_conf(layout, model.include_rpz, model.include_views),
        )
        self._write_common_conf(destination, env, proxy=model.proxy)
        self._write_native(
            destination,
            layout.conf_d / "20-options.conf",
            self.config_factory.proxy_options(env, layout)
            if model.proxy
            else self.config_factory.authoritative_options(env, layout),
        )

        if model.include_rpz:
            self._write_native(
                destination, layout.conf_d / "50-rpz.conf", self.config_factory.rpz_with_layout(env, layout)
            )
            self._write_native(
                destination, layout.rpz_data_dir / "rpz.local.zone", self.config_factory.rpz_local_zone(layout)
            )
        elif not model.proxy:
            self._write_native(
                destination, layout.conf_d / "50-rpz.conf", "// RPZ is disabled for this authoritative profile.\n"
            )

        if model.include_views:
            self._write_views(
                destination,
                ServerProfile.PROXY_HYBRID if model.proxy else ServerProfile.AUTHORITATIVE,
                include_rpz=model.include_rpz,
            )

    def _write_common_conf(self, destination: Path, env: dict[str, str], proxy: bool) -> None:
        layout = self.layout
        self._write_native(destination, layout.conf_d / "00-acl.conf", self.config_factory.acl(env, layout))
        self._write_native(destination, layout.conf_d / "10-keys.conf", self.config_factory.keys(env, layout))
        self._write_native(destination, layout.tsig_dir / "rndc.key", self.config_factory.keys(env, layout))
        self._write_native(destination, layout.conf_d / "30-logging.conf", self.config_factory.logging(layout))
        self._write_native(destination, layout.conf_d / "40-controls.conf", self.config_factory.controls(env, layout))
        self._write_native(destination, layout.conf_d / "45-statistics.conf", self.config_factory.statistics(layout))

    def _write_views(self, destination: Path, profile: ServerProfile, include_rpz: bool = False) -> None:
        layout = self.layout
        self._write_native(
            destination, layout.conf_d / "60-views.conf", self.config_factory.views(layout, include_rpz=include_rpz)
        )
        for view in ("external", "internal"):
            self._write_native(
                destination,
                layout.zones_enabled_dir(view) / "zones.index.conf",
                self.config_factory.zone_index(layout, view),
            )
            scope = ZoneScope.from_value(view)
            self._write_native(
                destination,
                layout.view_templates_dir(view) / "master.conf.tpl",
                self.config_factory.zone_template(layout, profile, scope, ZoneType.MASTER),
            )
            self._write_native(
                destination,
                layout.view_templates_dir(view) / "secondary.conf.tpl",
                self.config_factory.zone_template(layout, profile, scope, ZoneType.SECONDARY),
            )
            self._write_native(
                destination,
                layout.view_templates_dir(view) / "forward.conf.tpl",
                self.config_factory.zone_template(layout, profile, scope, ZoneType.FORWARD),
            )

    def _common_tree(self, destination: Path) -> None:
        layout = self.layout
        directories = [
            layout.config_dir,
            layout.conf_d,
            layout.views_dir,
            layout.external_view_dir,
            layout.internal_view_dir,
            layout.tsig_dir,
            layout.catalog_conf_dir,
            layout.data_dir,
            layout.master_data_dir,
            layout.master_view_data_dir("external"),
            layout.master_view_data_dir("internal"),
            layout.secondary_data_dir,
            layout.dynamic_data_dir,
            layout.rpz_data_dir,
            layout.statistics_data_dir,
            layout.cache_dir,
            layout.log_dir,
            layout.run_dir,
        ]
        for view in ("external", "internal"):
            directories.extend(
                [layout.zones_available_dir(view), layout.zones_enabled_dir(view), layout.view_templates_dir(view)]
            )
        for path in directories:
            self._mkdir_native(destination, path)

        for log_file in ("default.log", "security.log", "transfer.log", "rpz.log", "resolver.log", "query-errors.log"):
            self._write_native(destination, layout.log_dir / log_file, "")

        self._write_native(destination, layout.conf_d / "55-catalog.conf", self.config_factory.catalog_conf(layout))
        self._write_native(destination, layout.catalog_zone_file, self.config_factory.catalog_zone(layout))
        self._write_native(destination, layout.dynamic_data_dir / "managed-keys.bind", "")
        self._write_native(destination, layout.statistics_data_dir / "named_stats.txt", "")
        self._write_native(destination, layout.statistics_data_dir / "named.memstats", "")
        self._write_native(destination, layout.statistics_data_dir / "named_dump.db", "")
        if layout.sysconfig_file is not None:
            self._write_native(destination, layout.sysconfig_file, 'OPTIONS="-4"\n')
        if layout.systemd_override_dir is not None:
            self._write_native(
                destination, layout.systemd_override_dir / "override.conf", "[Service]\nLimitNOFILE=65536\n"
            )

    def _reset(self, destination: Path) -> None:
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True, exist_ok=True)

    def _native_path(self, destination: Path, native_path: Path) -> Path:
        return destination / native_path.relative_to("/")

    def _mkdir_native(self, destination: Path, native_path: Path) -> None:
        self._native_path(destination, native_path).mkdir(parents=True, exist_ok=True)

    def _write_native(self, destination: Path, native_path: Path, content: str) -> None:
        self._write(self._native_path(destination, native_path), content)

    def _write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.config_factory.adapt(content), encoding="utf-8")
