from __future__ import annotations
from dnsforge.domain.security.model import SecurityControls, SecurityProfile
from dnsforge.shared.errors import SettingsError

class SecuritySettingsValidator:
    def validate(self, settings: dict[str, str]) -> SecurityControls:
        profile = SecurityProfile.from_value(settings.get('SECURITY_PROFILE'))
        controls = SecurityControls.from_profile(profile)
        if profile is SecurityProfile.PARANOID and self._value(settings, 'ENABLE_RPZ') != 'yes':
            raise SettingsError('SECURITY_PROFILE=paranoid requires ENABLE_RPZ=yes')
        if profile.weight >= SecurityProfile.HARDENED.weight:
            if self._value(settings, 'ALLOW_RECURSION') == 'any':
                raise SettingsError('hardened or higher profiles must not allow recursion from any')
            if self._value(settings, 'BACK_RECURSIVE_CLIENTS') == 'any':
                raise SettingsError('hardened or higher profiles must not use BACK_RECURSIVE_CLIENTS=any')
        return controls

    def _value(self, settings: dict[str, str], key: str) -> str:
        return settings.get(key, '').strip().strip('\"\'').lower()
