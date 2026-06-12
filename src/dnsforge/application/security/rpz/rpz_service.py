from __future__ import annotations
from pathlib import Path
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader


class RpzService:
    def __init__(self, loader: EnvSettingsLoader | None = None) -> None:
        self.loader = loader or EnvSettingsLoader()

    def status(self, setup_file: Path) -> str:
        data = self.loader.load(setup_file) if setup_file.exists() else {}
        return f"RPZ: {data.get('ENABLE_RPZ', 'unknown').strip(chr(34)).strip(chr(39))}"

    def enable(self, setup_file: Path) -> str:
        return f"RPZ enable planned for {setup_file}"

    def update(self) -> str:
        return "RPZ update planned"

    def test(self, domain: str) -> str:
        return f"RPZ test planned: {domain}"
