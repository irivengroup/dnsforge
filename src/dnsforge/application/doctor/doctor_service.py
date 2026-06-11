from __future__ import annotations
from pathlib import Path

from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader


class DoctorService:
    def __init__(self, loader: EnvSettingsLoader | None = None) -> None:
        self.loader = loader or EnvSettingsLoader()

    def diagnose(self, setup_file: Path) -> str:
        settings = self.loader.load(setup_file) if setup_file.exists() else {}
        warnings: list[str] = []
        if settings.get("ENABLE_RRL", "no").strip("'\"") != "yes":
            warnings.append("RRL disabled: set ENABLE_RRL=yes")
        if settings.get("SECURITY_PROFILE", "enterprise").strip("'\"") in {"enterprise","paranoid"} and settings.get("ENABLE_DNSSEC", "no").strip("'\"") != "yes":
            warnings.append("DNSSEC disabled with enterprise/paranoid profile")
        if settings.get("BACK_RECURSIVE_CLIENTS", "").strip("'\"").lower() == "any":
            warnings.append("Recursive clients set to any: restrict ACLs")
        if settings.get("ENABLE_RPZ", "no").strip("'\"") != "yes" and settings.get("SECURITY_PROFILE", "").strip("'\"") == "paranoid":
            warnings.append("Paranoid profile requires RPZ")
        if not warnings:
            return "Doctor: no critical recommendation"
        return "\n".join(f"WARN: {w}" for w in warnings)
