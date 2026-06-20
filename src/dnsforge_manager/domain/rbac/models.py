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
NODE_OPERATOR = ManagerPermission(
    "manager:nodes:operate",
    "Submit operations to DNSForge nodes",
)
SYNC_OPERATOR = ManagerPermission(
    "manager:sync:operate",
    "Orchestrate cluster synchronization through DNSSync",
)
BEAT_READER = ManagerPermission("manager:dnsbeat:read", "Read DNSBeat monitoring data")
RBAC_ADMIN = ManagerPermission("manager:rbac:admin", "Manage Manager roles and permissions")
TRUST_ADMIN = ManagerPermission(
    "manager:trust:admin",
    "Approve, revoke and rotate DNSForge agent trust",
)
AUDIT_READER = ManagerPermission("manager:audit:read", "Read Manager audit events")
CHANGE_READER = ManagerPermission("manager:changes:read", "Read Manager change requests")
CHANGE_OPERATOR = ManagerPermission(
    "manager:changes:operate",
    "Create and dry-run Manager change requests",
)
CHANGE_ADMIN = ManagerPermission(
    "manager:changes:admin",
    "Approve, apply and rollback Manager change requests",
)

MANAGER_ADMIN_ROLE = ManagerRole(
    name="admin",
    permissions=(
        NODE_READER,
        NODE_OPERATOR,
        SYNC_OPERATOR,
        BEAT_READER,
        RBAC_ADMIN,
        TRUST_ADMIN,
        AUDIT_READER,
        CHANGE_READER,
        CHANGE_OPERATOR,
        CHANGE_ADMIN,
    ),
)

MANAGER_OPERATOR_ROLE = ManagerRole(
    name="operator",
    permissions=(NODE_READER, NODE_OPERATOR, SYNC_OPERATOR, BEAT_READER, CHANGE_READER, CHANGE_OPERATOR),
)

MANAGER_VIEWER_ROLE = ManagerRole(
    name="viewer",
    permissions=(NODE_READER, BEAT_READER, AUDIT_READER, CHANGE_READER),
)

MANAGER_ROLES = (MANAGER_ADMIN_ROLE, MANAGER_OPERATOR_ROLE, MANAGER_VIEWER_ROLE)
