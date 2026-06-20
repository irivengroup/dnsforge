from __future__ import annotations

from pathlib import Path

from dnsforge.domain.profile.model import ConfigurationProfile
from dnsforge.domain.profile.validator import ProfileSettingsValidator
from dnsforge.infrastructure.profile.template_loader import ProfileTemplateLoader
from dnsforge.infrastructure.profile.setup_profile_generator import SetupProfileGenerator
from dnsforge.shared.errors import SettingsError


class ProfileSetupTemplateService:
    """Render and install DNSForge setup.conf generated from profile policy.

    setup.conf is generated dynamically from SetupProfileGenerator. Legacy
    legacy profile resource templates are no longer consumed.
    """

    def __init__(
        self,
        loader: ProfileTemplateLoader | None = None,
        validator: ProfileSettingsValidator | None = None,
        generator: SetupProfileGenerator | None = None,
    ) -> None:
        self.loader = loader or ProfileTemplateLoader()
        self.validator = validator or ProfileSettingsValidator()
        self.generator = generator or SetupProfileGenerator()

    def template_text(self, profile: ConfigurationProfile) -> str:
        node = "srv01" if profile is ConfigurationProfile.AUTHORITATIVE else "srv02"
        return self.generator.generate(profile, node=node)

    def template_settings(self, profile: ConfigurationProfile) -> dict[str, str]:
        rendered = self.template_text(profile)
        settings = self._parse_rendered(rendered)
        self.validator.validate(profile, settings)
        return settings

    def render(self, profile: ConfigurationProfile, node: str, proxy_type: str | None = None) -> str:
        rendered = self.generator.generate(profile, node=node, proxy_type=proxy_type)
        self._validate_rendered(profile, rendered)
        return rendered

    def ensure_setup_file(
        self,
        profile: ConfigurationProfile,
        setup_file: Path,
        node: str,
        proxy_type: str | None = None,
        dry_run: bool = False,
    ) -> bool:
        """Ensure setup.conf exists for the requested profile.

        Returns True when the file would be or was created, False when an
        existing compatible setup.conf was kept.
        """
        if setup_file.exists():
            current = self.loader.load(setup_file)
            self.validator.validate(profile, current)
            return False

        rendered = self.render(profile, node, proxy_type=proxy_type)
        if dry_run:
            return True

        setup_file.parent.mkdir(parents=True, exist_ok=True)
        setup_file.write_text(rendered, encoding="utf-8")
        setup_file.chmod(0o640)
        return True

    def _parse_rendered(self, rendered: str) -> dict[str, str]:
        values: dict[str, str] = {}
        for line in rendered.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            values[key.strip()] = value.strip()
        return values

    def _validate_rendered(self, profile: ConfigurationProfile, rendered: str) -> None:
        try:
            self.validator.validate(profile, self._parse_rendered(rendered))
        except SettingsError:
            raise
