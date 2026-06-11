from __future__ import annotations


class DnsForgeError(RuntimeError):
    pass


class SettingsError(DnsForgeError):
    pass


class ConfigureError(DnsForgeError):
    pass


class ZoneError(DnsForgeError):
    pass
