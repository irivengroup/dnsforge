from __future__ import annotations
import socket
from pathlib import Path

from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader


class StatusService:
    def __init__(self, loader: EnvSettingsLoader | None = None) -> None:
        self.loader = loader or EnvSettingsLoader()

    def show(self, setup_file: Path) -> str:
        settings = self.loader.load(setup_file) if setup_file.exists() else {}
        role = settings.get("ROLE", "unknown").strip("'\"")
        proxy_type = settings.get("PROXY_TYPE", "").strip("'\"")
        security = settings.get("SECURITY_PROFILE", "enterprise").strip("'\"")
        profile = "authoritative" if role == "dns-authoritative" else f"proxy-{proxy_type or 'unknown'}"
        lines = [
            f"Hostname: {socket.gethostname()}",
            f"Role: {role}",
            f"Profile: {profile}",
            f"Security Profile: {security}",
            f"RPZ: {settings.get('ENABLE_RPZ', 'unknown').strip(chr(34)).strip(chr(39))}",
            f"DNSSEC: {settings.get('ENABLE_DNSSEC', 'unknown').strip(chr(34)).strip(chr(39))}",
            f"RRL: {settings.get('ENABLE_RRL', 'unknown').strip(chr(34)).strip(chr(39))}",
            f"Setup File: {setup_file}",
        ]
        return "\n".join(lines)
