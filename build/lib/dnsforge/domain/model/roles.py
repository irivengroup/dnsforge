from __future__ import annotations

from enum import Enum


class DnsRole(str, Enum):
    PROXY = "dns-proxy"
    AUTHORITATIVE = "dns-authoritative"
