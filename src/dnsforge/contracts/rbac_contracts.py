from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Permission:
    name: str
    description: str


@dataclass(frozen=True)
class RoleContract:
    name: str
    permissions: tuple[Permission, ...]


ROOT_OPERATOR_ROLE = RoleContract(
    name="root-operator",
    permissions=(
        Permission("dnsforge:local-cli", "Run local DNSForge CLI commands with elevated privileges."),
        Permission("dnsforge:read", "Read local DNSForge state."),
        Permission("dnsforge:write", "Change local DNSForge-managed BIND state."),
        Permission("dnsforge:restore", "Restore local DNSForge backups and disaster snapshots."),
    ),
)
