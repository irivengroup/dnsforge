from __future__ import annotations


class DnsForgeError(RuntimeError):
    pass


class SettingsError(DnsForgeError):
    pass


class InitializeError(DnsForgeError):
    pass


class ZoneError(DnsForgeError):
    pass
