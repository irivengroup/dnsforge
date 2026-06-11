from __future__ import annotations
from pathlib import Path
from dnsforge.domain.security.validator import SecuritySettingsValidator
from dnsforge.infrastructure.settings.env_loader import EnvSettingsLoader

class SecurityService:
    def __init__(self, loader: EnvSettingsLoader | None = None, validator: SecuritySettingsValidator | None = None) -> None:
        self.loader = loader or EnvSettingsLoader()
        self.validator = validator or SecuritySettingsValidator()

    def load_controls(self, setup_file: Path):
        return self.validator.validate(self.loader.load(setup_file))

    def show(self, setup_file: Path) -> str:
        controls = self.load_controls(setup_file)
        lines = [f'Profile: {controls.profile.value}', f'Score: {controls.score()}/100', '', 'Controls:']
        for name, enabled in controls.enabled_controls().items():
            lines.append(f'  {name}: {"enabled" if enabled else "disabled"}')
        return '\n'.join(lines)

    def audit(self, setup_file: Path) -> tuple[bool, str]:
        controls = self.load_controls(setup_file)
        lines = [f'Security profile: {controls.profile.value}', f'Security score: {controls.score()}/100', '']
        for name, enabled in controls.enabled_controls().items():
            lines.append(f'{name}: {"OK" if enabled else "WARN"}')
        return True, '\n'.join(lines)
