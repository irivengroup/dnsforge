from __future__ import annotations

from pathlib import Path

from dnsforge.domain.profile.model import ConfigurationProfile
from dnsforge.domain.profile.validator import ProfileSettingsValidator
from dnsforge.infrastructure.profile.template_loader import ProfileTemplateLoader


class ProfileAuditor:
    def __init__(
        self,
        loader: ProfileTemplateLoader | None = None,
        validator: ProfileSettingsValidator | None = None,
    ) -> None:
        self.loader = loader or ProfileTemplateLoader()
        self.validator = validator or ProfileSettingsValidator()

    def audit_templates(self, project_root: Path) -> list[str]:
        errors: list[str] = []
        template_root = project_root / "install" / "templates"

        for profile in ConfigurationProfile:
            path = template_root / profile.value / "setup.conf"
            if not path.exists():
                errors.append(f"missing template: {path}")
                continue

            try:
                self.validator.validate(profile, self.loader.load(path))
            except Exception as exc:
                errors.append(f"{profile.value}: {exc}")

        return errors
