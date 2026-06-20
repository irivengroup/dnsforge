from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BindLayout:
    """Native Enterprise BIND filesystem layout for the local platform.

    DNSForge owns BIND deployment/configuration, but /etc/dnsforge remains
    reserved for DNSForge node configuration only. Runtime DNS configuration,
    zones, keys, statistics and logs are deployed directly to the native BIND
    tree for the detected distribution family.
    """

    family: str
    service_name: str
    named_conf: Path
    config_dir: Path
    data_dir: Path
    cache_dir: Path
    run_dir: Path
    log_dir: Path
    sysconfig_file: Path | None = None
    systemd_override_dir: Path | None = None

    @property
    def conf_d(self) -> Path:
        return self.config_dir / "conf.d"

    @property
    def views_dir(self) -> Path:
        return self.config_dir / "views"

    @property
    def tsig_dir(self) -> Path:
        return self.config_dir / "tsig"

    @property
    def catalog_conf_dir(self) -> Path:
        return self.config_dir / "catalog"

    @property
    def external_view_dir(self) -> Path:
        return self.views_dir / "external"

    @property
    def internal_view_dir(self) -> Path:
        return self.views_dir / "internal"

    def view_dir(self, view: str) -> Path:
        return self.views_dir / view

    def zones_available_dir(self, view: str) -> Path:
        return self.view_dir(view) / "zones.available"

    def zones_enabled_dir(self, view: str) -> Path:
        return self.view_dir(view) / "zones.enabled"

    def view_templates_dir(self, view: str) -> Path:
        return self.view_dir(view) / "templates"

    @property
    def master_data_dir(self) -> Path:
        return self.data_dir / "master"

    def master_view_data_dir(self, view: str) -> Path:
        return self.master_data_dir / view

    @property
    def secondary_data_dir(self) -> Path:
        return self.data_dir / "secondary"

    @property
    def dynamic_data_dir(self) -> Path:
        return self.data_dir / "dynamic"

    @property
    def rpz_data_dir(self) -> Path:
        return self.data_dir / "rpz"

    @property
    def statistics_data_dir(self) -> Path:
        return self.data_dir / "data"

    @property
    def catalog_zone_file(self) -> Path:
        return self.catalog_conf_dir / "catalog.zone"

    @property
    def dnssec_key_dir(self) -> Path:
        """Default writable DNSSEC key directory for this BIND layout."""
        return self.data_dir / "dnssec"

    @property
    def backup_paths(self) -> tuple[Path, ...]:
        paths = [
            self.named_conf,
            self.config_dir,
            self.data_dir,
            self.cache_dir,
            self.log_dir,
            Path("/etc/rndc.conf"),
            Path("/etc/rndc.key"),
        ]
        if self.sysconfig_file:
            paths.append(self.sysconfig_file)
        if self.systemd_override_dir:
            paths.append(self.systemd_override_dir)
        return tuple(dict.fromkeys(paths))

    @property
    def selinux_paths(self) -> tuple[Path, ...]:
        return tuple(dict.fromkeys((self.named_conf, self.config_dir, self.data_dir, self.log_dir, self.run_dir)))


class BindLayoutDetector:
    """Detect the native BIND layout.

    Environment override is intentionally supported for tests and image builds:
      DNSFORGE_BIND_LAYOUT=redhat|debian|suse
    """

    def detect(self) -> BindLayout:
        override = os.environ.get("DNSFORGE_BIND_LAYOUT", "").strip().lower()
        if override:
            return self.from_family(override)

        os_release = self._read_os_release()
        distro_id = os_release.get("ID", "").lower()
        like = os_release.get("ID_LIKE", "").lower()
        probe = f"{distro_id} {like}"

        if any(token in probe for token in ("debian", "ubuntu")):
            return self.from_family("debian")
        if any(token in probe for token in ("suse", "sles", "opensuse")):
            return self.from_family("suse")
        return self.from_family("redhat")

    def from_family(self, family: str) -> BindLayout:
        family = family.lower()
        if family in {"debian", "ubuntu"}:
            return BindLayout(
                family="debian",
                service_name="bind9",
                named_conf=Path("/etc/bind/named.conf"),
                config_dir=Path("/etc/bind"),
                data_dir=Path("/var/lib/bind"),
                cache_dir=Path("/var/cache/bind"),
                run_dir=Path("/run/named"),
                log_dir=Path("/var/log/named"),
                sysconfig_file=Path("/etc/default/named"),
                systemd_override_dir=Path("/etc/systemd/system/bind9.service.d"),
            )
        if family in {"suse", "sles", "opensuse"}:
            return BindLayout(
                family="suse",
                service_name="named",
                named_conf=Path("/etc/named.conf"),
                config_dir=Path("/etc/named"),
                data_dir=Path("/var/lib/named"),
                cache_dir=Path("/var/lib/named/dyn"),
                run_dir=Path("/run/named"),
                log_dir=Path("/var/log/named"),
                sysconfig_file=Path("/etc/sysconfig/named"),
                systemd_override_dir=Path("/etc/systemd/system/named.service.d"),
            )
        if family in {"redhat", "rhel", "rocky", "alma", "centos", "fedora"}:
            return BindLayout(
                family="redhat",
                service_name="named",
                named_conf=Path("/etc/named.conf"),
                config_dir=Path("/etc/named"),
                data_dir=Path("/var/named"),
                cache_dir=Path("/var/named/data"),
                run_dir=Path("/run/named"),
                log_dir=Path("/var/log/named"),
                sysconfig_file=Path("/etc/sysconfig/named"),
                systemd_override_dir=Path("/etc/systemd/system/named.service.d"),
            )
        raise ValueError(f"unsupported BIND layout family: {family}")

    def _read_os_release(self) -> dict[str, str]:
        path = Path("/etc/os-release")
        if not path.exists():
            return {}
        result: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "=" not in line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            result[key] = value.strip().strip('"')
        return result
