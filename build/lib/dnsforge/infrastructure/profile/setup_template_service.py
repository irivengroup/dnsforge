from __future__ import annotations

from importlib import resources
from pathlib import Path

from dnsforge.domain.profile.model import ConfigurationProfile
from dnsforge.domain.profile.validator import ProfileSettingsValidator
from dnsforge.infrastructure.profile.template_loader import ProfileTemplateLoader
from dnsforge.shared.errors import SettingsError


class ProfileSetupTemplateService:
    """Render and install DNSForge setup.conf templates bundled with the package.

    The setup.conf templates are product resources, not installer assets. They are
    selected by DNS profile and are applied by the DNSForge CLI during profile
    initialization.
    """

    _RESOURCE_PACKAGE = "dnsforge.infrastructure.profile.resources"

    def __init__(
        self,
        loader: ProfileTemplateLoader | None = None,
        validator: ProfileSettingsValidator | None = None,
    ) -> None:
        self.loader = loader or ProfileTemplateLoader()
        self.validator = validator or ProfileSettingsValidator()

    def template_text(self, profile: ConfigurationProfile) -> str:
        template = resources.files(self._RESOURCE_PACKAGE).joinpath(profile.value).joinpath("setup.conf")
        return template.read_text(encoding="utf-8")

    def template_settings(self, profile: ConfigurationProfile) -> dict[str, str]:
        template = resources.files(self._RESOURCE_PACKAGE).joinpath(profile.value).joinpath("setup.conf")
        with resources.as_file(template) as path:
            settings = self.loader.load(path)
        self.validator.validate(profile, settings)
        return settings

    def render(self, profile: ConfigurationProfile, node: str, proxy_type: str | None = None) -> str:
        text = self.template_text(profile)
        lines: list[str] = []
        replaced_node = False
        replaced_proxy_type = False

        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("NODE_NAME="):
                lines.append(f'NODE_NAME="{node}"')
                replaced_node = True
                continue
            if stripped.startswith("PROXY_TYPE=") and profile is not ConfigurationProfile.AUTHORITATIVE:
                value = proxy_type or profile.proxy_type or "hybrid"
                lines.append(f'PROXY_TYPE="{value}"')
                replaced_proxy_type = True
                continue
            lines.append(line)

        if not replaced_node:
            lines.append(f'NODE_NAME="{node}"')
        if profile is not ConfigurationProfile.AUTHORITATIVE and not replaced_proxy_type:
            value = proxy_type or profile.proxy_type or "hybrid"
            lines.append(f'PROXY_TYPE="{value}"')

        rendered = "\n".join(lines).rstrip() + "\n"
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

    def _validate_rendered(self, profile: ConfigurationProfile, rendered: str) -> None:
        values: dict[str, str] = {}
        for line in rendered.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            values[key.strip()] = value.strip()
        try:
            self.validator.validate(profile, values)
        except SettingsError:
            raise
