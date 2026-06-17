from __future__ import annotations

from dnsforge.domain.profile.model import ConfigurationProfile
from dnsforge.shared.errors import SettingsError


class ProfileSettingsValidator:
    BOOL_VALUES = {"yes", "no"}

    def validate(self, profile: ConfigurationProfile, settings: dict[str, str]) -> None:
        if profile is ConfigurationProfile.AUTHORITATIVE:
            self._validate_authoritative(settings)
        elif profile is ConfigurationProfile.PROXY_FORWARDER:
            self._validate_proxy_forwarder(settings)
        elif profile is ConfigurationProfile.PROXY_HYBRID:
            self._validate_proxy_hybrid(settings)
        else:
            raise SettingsError(f"unsupported profile: {profile}")

    def _validate_authoritative(self, settings: dict[str, str]) -> None:
        self._require_equal(settings, "ROLE", "dns-authoritative")
        self._forbid(settings, "PROXY_TYPE")
        self._require_not_yes(settings, "ENABLE_RPZ", "authoritative profile must not enable RPZ")
        for key in (
            "ENABLE_PROXY_MASTER_ZONES",
            "ENABLE_PROXY_AUTHORITATIVE_ZONES",
            "ENABLE_PROXY_LOCAL_ZONES",
            "ENABLE_PROXY_HA",
        ):
            self._require_not_yes(settings, key, f"authoritative profile must not enable {key}")

    def _validate_proxy_forwarder(self, settings: dict[str, str]) -> None:
        self._require_equal(settings, "ROLE", "dns-proxy")
        self._require_equal(settings, "PROXY_TYPE", "forwarder")
        for key in (
            "ENABLE_PROXY_MASTER_ZONES",
            "ENABLE_PROXY_AUTHORITATIVE_ZONES",
            "ENABLE_PROXY_LOCAL_ZONES",
        ):
            self._require_not_yes(settings, key, f"forwarder profile must not enable {key}")

    def _validate_proxy_hybrid(self, settings: dict[str, str]) -> None:
        self._require_equal(settings, "ROLE", "dns-proxy")
        self._require_equal(settings, "PROXY_TYPE", "hybrid")

    def _require_equal(self, settings: dict[str, str], key: str, expected: str) -> None:
        actual = self._normalized(settings.get(key))
        if actual != expected:
            raise SettingsError(f"{key} must be {expected!r}, got {actual!r}")

    def _forbid(self, settings: dict[str, str], key: str) -> None:
        if key in settings and self._normalized(settings.get(key)):
            raise SettingsError(f"{key} is not allowed for this profile")

    def _require_not_yes(self, settings: dict[str, str], key: str, message: str) -> None:
        if self._normalized(settings.get(key, "no")) == "yes":
            raise SettingsError(message)

    def _normalized(self, value: str | None) -> str:
        if value is None:
            return ""
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        return value.strip()
