from __future__ import annotations

from pathlib import Path

from dnsforge.application.network.interface_diagnostics_service import InterfaceDiagnosticsService
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader


class DoctorService:
    def __init__(self, loader: EnvSettingsLoader | None = None) -> None:
        self.loader = loader or EnvSettingsLoader()

    def diagnose(self, setup_file: Path) -> str:
        settings = self.loader.load(setup_file) if setup_file.exists() else {}
        warnings: list[str] = []
        if settings.get("ENABLE_RRL", "no").strip("'\"") != "yes":
            warnings.append("RRL disabled: set ENABLE_RRL=yes")
        if (
            settings.get("SECURITY_PROFILE", "enterprise").strip("'\"") in {"enterprise", "paranoid"}
            and settings.get("ENABLE_DNSSEC", "no").strip("'\"") != "yes"
        ):
            warnings.append("DNSSEC disabled with enterprise/paranoid profile")
        if settings.get("BACK_RECURSIVE_CLIENTS", "").strip("'\"").lower() == "any":
            warnings.append("Recursive clients set to any: restrict ACLs")
        if (
            settings.get("ENABLE_RPZ", "no").strip("'\"") != "yes"
            and settings.get("SECURITY_PROFILE", "").strip("'\"") == "paranoid"
        ):
            warnings.append("Paranoid profile requires RPZ")
        warnings.extend(self._network_warnings(setup_file))
        if not warnings:
            return "Doctor: no critical recommendation"
        return "\n".join(f"WARN: {w}" for w in warnings)

    def _network_warnings(self, setup_file: Path) -> list[str]:
        if not setup_file.exists():
            return ["Network diagnostics unavailable: setup file not found"]
        try:
            payload = InterfaceDiagnosticsService(setup_file).as_dict()
        except Exception as exc:  # pragma: no cover - defensive operational diagnosis path
            return [f"Network diagnostics failed: {exc}"]
        distinct_ips = payload.get("distinct_bind_ips")
        interfaces = payload.get("interfaces")
        warnings: list[str] = []
        if isinstance(distinct_ips, list) and len(distinct_ips) == 1:
            warnings.append("All BIND planes resolve to one IPv4 address; validate single-NIC topology intentionally")
        if isinstance(interfaces, dict):
            unresolved = []
            for role in ("extranet", "intranet", "admin"):
                item = interfaces.get(role)
                if isinstance(item, dict) and not item.get("ip"):
                    unresolved.append(role)
            if unresolved:
                warnings.append("Unresolved BIND interface planes: " + ", ".join(unresolved))
        return warnings
