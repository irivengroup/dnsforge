from __future__ import annotations

from dnsforge.domain.profile.model import ConfigurationProfile
from dnsforge.domain.profile.validator import ProfileSettingsValidator
from dnsforge.infrastructure.profile.setup_template_service import ProfileSetupTemplateService
from dnsforge.infrastructure.profile.template_loader import ProfileTemplateLoader


class ProfileAuditor:
    def __init__(
        self,
        template_service: ProfileSetupTemplateService | None = None,
        loader: ProfileTemplateLoader | None = None,
        validator: ProfileSettingsValidator | None = None,
    ) -> None:
        self.template_service = template_service or ProfileSetupTemplateService(loader=loader, validator=validator)

    def audit_templates(self) -> list[str]:
        errors: list[str] = []

        for profile in ConfigurationProfile:
            try:
                self.template_service.template_settings(profile)
            except Exception as exc:
                errors.append(f"{profile.value}: {exc}")

        return errors
