from __future__ import annotations

from pathlib import Path

from dnsforge.domain.health.model import HealthCheck, HealthReport
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader


class HealthService:
    def __init__(self, loader: EnvSettingsLoader | None = None) -> None:
        self.loader = loader or EnvSettingsLoader()

    def check(self, setup_file: Path, project_root: Path) -> HealthReport:
        checks: list[HealthCheck] = []
        checks.append(HealthCheck("setup.conf", setup_file.exists(), str(setup_file)))

        try:
            settings = self.loader.load(setup_file) if setup_file.exists() else {}
            checks.append(HealthCheck("settings parse", bool(settings), f"{len(settings)} variables"))
        except Exception as exc:
            settings = {}
            checks.append(HealthCheck("settings parse", False, str(exc)))

        from dnsforge.infrastructure.filesystem.paths import ProjectPaths

        catalog = ProjectPaths(project_root).catalog_file
        checks.append(HealthCheck("zone catalog", catalog.exists(), "configured" if catalog.exists() else "missing"))
        checks.append(
            HealthCheck(
                "role",
                settings.get("ROLE", "").strip("'\"") in {"dns-proxy", "dns-authoritative"},
                settings.get("ROLE", ""),
            )
        )
        checks.append(
            HealthCheck(
                "security profile",
                settings.get("SECURITY_PROFILE", "enterprise").strip("'\"")
                in {"standard", "hardened", "enterprise", "paranoid"},
                settings.get("SECURITY_PROFILE", "enterprise"),
            )
        )
        checks.append(
            HealthCheck(
                "rpz value",
                settings.get("ENABLE_RPZ", "no").strip("'\"") in {"yes", "no"},
                settings.get("ENABLE_RPZ", "no"),
            )
        )
        return HealthReport(checks)
