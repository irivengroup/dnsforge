from __future__ import annotations

from pathlib import Path
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader


class DnssecService:
    def __init__(self, loader: EnvSettingsLoader | None = None) -> None:
        self.loader = loader or EnvSettingsLoader()

    def status(self, setup_file: Path) -> str:
        data = self.loader.load(setup_file) if setup_file.exists() else {}
        return f"DNSSEC: {data.get('ENABLE_DNSSEC', 'unknown').strip(chr(34)).strip(chr(39))}"

    def validate(self, setup_file: Path) -> str:
        data = self.loader.load(setup_file) if setup_file.exists() else {}
        enabled = data.get("ENABLE_DNSSEC", "no").strip("'\"").lower()
        return "DNSSEC validation OK" if enabled == "yes" else "DNSSEC validation WARN: disabled"

    def rotate_ksk(self) -> str:
        return "DNSSEC KSK rotation planned"

    def rotate_zsk(self) -> str:
        return "DNSSEC ZSK rotation planned"

    def check_expiry(self) -> str:
        return "DNSSEC key expiry check planned"
