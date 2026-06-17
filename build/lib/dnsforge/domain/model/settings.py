from __future__ import annotations

from dataclasses import dataclass, field

from dnsforge.domain.model.proxy_type import ProxyType
from dnsforge.domain.model.roles import DnsRole


@dataclass(frozen=True)
class BaseSettings:
    role: DnsRole
    node_name: str
    raw: dict[str, str] = field(repr=False)

    def to_env(self) -> dict[str, str]:
        data = dict(self.raw)
        data["ROLE"] = self.role.value
        data["NODE_NAME"] = self.node_name
        return data


@dataclass(frozen=True)
class ProxySettings(BaseSettings):
    proxy_type: ProxyType

    def to_env(self) -> dict[str, str]:
        data = super().to_env()
        data["PROXY_TYPE"] = self.proxy_type.value
        return data


@dataclass(frozen=True)
class AuthoritativeSettings(BaseSettings):
    pass
