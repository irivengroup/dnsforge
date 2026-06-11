from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from dnsforge.domain.model.settings import AuthoritativeSettings, ProxySettings
from dnsforge.domain.render.profile import ProxyRenderProfile
from dnsforge.domain.security.model import SecurityControls, SecurityProfile
from dnsforge.infrastructure.bind.layout import BindLayout, BindLayoutDetector
from dnsforge.infrastructure.security.bind_security import BindSecurityOptionsRenderer
from dnsforge.infrastructure.templates.service import TemplateService


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

    def build_proxy_configuration(self, settings: dict[str, str], layout: BindLayout, include_views: bool) -> BindConfiguration:
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
        if include_rpz:
            includes.append(layout.conf_d / "50-rpz.conf")
        if include_views:
            includes.append(layout.conf_d / "60-views.conf")
        include_block = "\n".join(f'include "{path}";' for path in includes)
        return self._render("bind/named.conf.j2", {"INCLUDES": include_block}, layout)

    def acl(self, settings: dict[str, str], layout: BindLayout | None = None) -> str:
        layout = layout or self.template_service.layout
        return self._render(
            "bind/00-acl.conf.j2",
            {
                "RECURSIVE_CLIENTS": settings.get("BACK_RECURSIVE_CLIENTS", "localnets; localhost;"),
                "ADMIN_CLIENTS": settings.get("ADM_ALLOWED_CLIENTS", "localhost;"),
                "ZONE_TRANSFER_CLIENTS": settings.get("XFR_ALLOWED_CLIENTS", "none;"),
            },
            layout,
        )

    def _options(self, settings: dict[str, str], layout: BindLayout, proxy: bool) -> str:
        controls = self.security_controls(settings)
        return self._render(
            "bind/20-options.conf.j2",
            {
                "DATA_DIR": layout.data_dir,
                "DUMP_FILE": layout.statistics_data_dir / "named_dump.db",
                "STATISTICS_FILE": layout.statistics_data_dir / "named_stats.txt",
                "MEMSTATISTICS_FILE": layout.statistics_data_dir / "named.memstats",
                "RECURSION": "yes" if proxy else "no",
                "ALLOW_RECURSION": "recursive_clients; localhost;" if proxy else "none;",
                "ALLOW_QUERY_CACHE": "recursive_clients; localhost;" if proxy else "none;",
                "AUTHORITATIVE_POLICY": "" if proxy else "allow-query { any; };\n    allow-transfer { zone_transfer_clients; };",
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
            "\n".join([
                f'key "{key_name}" {{',
                "    algorithm hmac-sha256;",
                f'    secret "{secret}";',
                "};",
            ])
        ]
        xfr_key = settings.get("XFR_TSIG_KEY_NAME")
        xfr_secret = settings.get("XFR_TSIG_SECRET")
        if xfr_key and xfr_secret:
            blocks.append("\n".join([
                f'key "{xfr_key}" {{',
                "    algorithm hmac-sha256;",
                f'    secret "{xfr_secret}";',
                "};",
            ]))
        return self._render("bind/10-keys.conf.j2", {"KEY_BLOCKS": "\n\n".join(blocks)}, layout)

    def controls(self, settings: dict[str, str], layout: BindLayout | None = None) -> str:
        layout = layout or self.template_service.layout
        return self._render("bind/40-controls.conf.j2", {"RNDC_KEY_NAME": settings.get("RNDC_KEY_NAME", "rndc-key")}, layout)

    def forwarders(self, settings: dict[str, str]) -> str:
        return "\n".join(["forwarders {", f'    {settings.get("DNS_FORWARDERS", "8.8.8.8; 1.1.1.1;")}', "};", ""])

    def rpz(self, settings: dict[str, str]) -> str:
        return self.rpz_with_layout(settings, self.template_service.layout)

    def rpz_with_layout(self, settings: dict[str, str], layout: BindLayout) -> str:
        if settings.get("ENABLE_RPZ", "no") != "yes":
            return ""
        zone = settings.get("RPZ_ZONE_NAME", "rpz.local")
        block = "\n".join([
            "response-policy {",
            f'    zone "{zone}";',
            "};",
            "",
            f'zone "{zone}" {{',
            "    type master;",
            f'    file "{layout.rpz_data_dir / "rpz.local.zone"}";',
            "    allow-query { localhost; admin_clients; };",
            "};",
            "",
        ])
        return self._render("bind/50-rpz.conf.j2", {"RPZ_BLOCK": block}, layout)

    def logging(self, layout: BindLayout) -> str:
        return self._render("bind/30-logging.conf.j2", {"LOG_DIR": layout.log_dir}, layout)

    def statistics(self, layout: BindLayout | None = None) -> str:
        layout = layout or self.template_service.layout
        return self._render("bind/45-statistics.conf.j2", {}, layout)

    def views(self, layout: BindLayout) -> str:
        return self._render(
            "bind/60-views.conf.j2",
            {
                "INTERNAL_ZONE_INDEX": layout.zones_enabled_dir("internal") / "zones.index.conf",
                "EXTERNAL_ZONE_INDEX": layout.zones_enabled_dir("external") / "zones.index.conf",
            },
            layout,
        )

    def zone_index(self, layout: BindLayout, view: str) -> str:
        return f"// DNSForge managed index for {view} view.\n"

    def master_template(self, layout: BindLayout, view: str) -> str:
        return self._render(
            "bind/master-zone.conf.tpl",
            {"MASTER_ZONE_FILE": f"{layout.master_view_data_dir(view)}/{{{{ zone_file }}}}"},
            layout,
        )

    def secondary_template(self, layout: BindLayout) -> str:
        return self._render(
            "bind/secondary-zone.conf.tpl",
            {"SECONDARY_ZONE_FILE": f"{layout.secondary_data_dir}/{{{{ zone_file }}}}"},
            layout,
        )

    def forward_template(self, layout: BindLayout | None = None) -> str:
        layout = layout or self.template_service.layout
        return self._render("bind/forward-zone.conf.tpl", {}, layout)

    def catalog_zone(self, layout: BindLayout | None = None) -> str:
        layout = layout or self.template_service.layout
        return self._render("bind/catalog.zone.j2", {}, layout)

    def rpz_local_zone(self, layout: BindLayout | None = None) -> str:
        layout = layout or self.template_service.layout
        return self._render("bind/rpz.local.zone.j2", {}, layout)


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
        self._write_native(destination, layout.named_conf, self.config_factory.named_conf(layout, model.include_rpz, model.include_views))
        self._write_common_conf(destination, env, proxy=model.proxy)
        self._write_native(
            destination,
            layout.conf_d / "20-options.conf",
            self.config_factory.proxy_options(env, layout) if model.proxy else self.config_factory.authoritative_options(env, layout),
        )

        if model.include_rpz:
            self._write_native(destination, layout.conf_d / "50-rpz.conf", self.config_factory.rpz_with_layout(env, layout))
            self._write_native(destination, layout.rpz_data_dir / "rpz.local.zone", self.config_factory.rpz_local_zone(layout))
        elif not model.proxy:
            self._write_native(destination, layout.conf_d / "50-rpz.conf", "// RPZ is disabled for this authoritative profile.\n")

        if model.include_views:
            self._write_views(destination)

    def _write_common_conf(self, destination: Path, env: dict[str, str], proxy: bool) -> None:
        layout = self.layout
        self._write_native(destination, layout.conf_d / "00-acl.conf", self.config_factory.acl(env, layout))
        self._write_native(destination, layout.conf_d / "10-keys.conf", self.config_factory.keys(env, layout))
        self._write_native(destination, layout.tsig_dir / "rndc.key", self.config_factory.keys(env, layout))
        self._write_native(destination, layout.conf_d / "30-logging.conf", self.config_factory.logging(layout))
        self._write_native(destination, layout.conf_d / "40-controls.conf", self.config_factory.controls(env, layout))
        self._write_native(destination, layout.conf_d / "45-statistics.conf", self.config_factory.statistics(layout))

    def _write_views(self, destination: Path) -> None:
        layout = self.layout
        self._write_native(destination, layout.conf_d / "60-views.conf", self.config_factory.views(layout))
        for view in ("external", "internal"):
            self._write_native(destination, layout.zones_enabled_dir(view) / "zones.index.conf", self.config_factory.zone_index(layout, view))
            self._write_native(destination, layout.view_templates_dir(view) / "master.conf.tpl", self.config_factory.master_template(layout, view))
            self._write_native(destination, layout.view_templates_dir(view) / "secondary.conf.tpl", self.config_factory.secondary_template(layout))
            self._write_native(destination, layout.view_templates_dir(view) / "forward.conf.tpl", self.config_factory.forward_template(layout))

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
            directories.extend([layout.zones_available_dir(view), layout.zones_enabled_dir(view), layout.view_templates_dir(view)])
        for path in directories:
            self._mkdir_native(destination, path)

        for log_file in ("default.log", "security.log", "transfer.log", "rpz.log", "resolver.log"):
            self._write_native(destination, layout.log_dir / log_file, "")

        self._write_native(destination, layout.catalog_zone_file, self.config_factory.catalog_zone(layout))
        self._write_native(destination, layout.dynamic_data_dir / "managed-keys.bind", "")
        self._write_native(destination, layout.statistics_data_dir / "named_stats.txt", "")
        self._write_native(destination, layout.statistics_data_dir / "named.memstats", "")
        self._write_native(destination, layout.statistics_data_dir / "named_dump.db", "")
        if layout.sysconfig_file is not None:
            self._write_native(destination, layout.sysconfig_file, 'OPTIONS="-4"\n')
        if layout.systemd_override_dir is not None:
            self._write_native(destination, layout.systemd_override_dir / "override.conf", "[Service]\nLimitNOFILE=65536\n")

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
