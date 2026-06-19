from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ManagerPermission:
    name: str
    description: str


@dataclass(frozen=True)
class ManagerRole:
    name: str
    permissions: tuple[ManagerPermission, ...]

    def allows(self, permission_name: str) -> bool:
        return any(permission.name == permission_name for permission in self.permissions)


NODE_READER = ManagerPermission("manager:nodes:read", "Read managed DNSForge nodes")
NODE_OPERATOR = ManagerPermission("manager:nodes:operate", "Submit operations to DNSForge nodes")
SYNC_OPERATOR = ManagerPermission("manager:sync:operate", "Orchestrate cluster synchronization through DNSSync")
BEAT_READER = ManagerPermission("manager:dnsbeat:read", "Read DNSBeat monitoring data")
RBAC_ADMIN = ManagerPermission("manager:rbac:admin", "Manage Manager roles and permissions")
TRUST_ADMIN = ManagerPermission("manager:trust:admin", "Approve, revoke and rotate DNSForge agent trust")
AUDIT_READER = ManagerPermission("manager:audit:read", "Read Manager audit events")

MANAGER_ADMIN_ROLE = ManagerRole(
    name="admin",
    permissions=(NODE_READER, NODE_OPERATOR, SYNC_OPERATOR, BEAT_READER, RBAC_ADMIN, TRUST_ADMIN, AUDIT_READER),
)

MANAGER_OPERATOR_ROLE = ManagerRole(
    name="operator",
    permissions=(NODE_READER, NODE_OPERATOR, SYNC_OPERATOR, BEAT_READER),
)

MANAGER_VIEWER_ROLE = ManagerRole(
    name="viewer",
    permissions=(NODE_READER, BEAT_READER, AUDIT_READER),
)

MANAGER_ROLES = (MANAGER_ADMIN_ROLE, MANAGER_OPERATOR_ROLE, MANAGER_VIEWER_ROLE)
