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
SYNC_READER = ManagerPermission("manager:sync:read", "Read DNSSync orchestration state")
SYNC_OPERATOR = ManagerPermission(
    "manager:sync:operate",
    "Plan, validate and dry-run DNSSync orchestration",
)
SYNC_ADMIN = ManagerPermission(
    "manager:sync:admin",
    "Apply and rollback DNSSync orchestration plans",
)
BEAT_READER = ManagerPermission("manager:dnsbeat:read", "Read DNSBeat monitoring data")
RBAC_ADMIN = ManagerPermission("manager:rbac:admin", "Manage Manager roles and permissions")
TRUST_READER = ManagerPermission("manager:trust:read", "Read DNSForge agent trust state")
TRUST_WRITER = ManagerPermission("manager:trust:write", "Create DNSForge agent enrollment requests")
TRUST_ADMIN = ManagerPermission(
    "manager:trust:admin",
    "Approve, revoke and rotate DNSForge agent trust",
)
AUDIT_READER = ManagerPermission("manager:audit:read", "Read Manager audit events")
INVENTORY_READER = ManagerPermission("manager:inventory:read", "Read Central Inventory objects")
INVENTORY_WRITER = ManagerPermission(
    "manager:inventory:write",
    "Create Central Inventory objects and update agent status",
)

COMPLIANCE_READER = ManagerPermission(
    "manager:compliance:read",
    "Read Manager compliance aggregation and drift reports",
)
COMPLIANCE_OPERATOR = ManagerPermission(
    "manager:compliance:operate",
    "Submit DNS compliance repair operations through DNSForge agents",
)
TRUST_APPROVER = ManagerPermission(
    "manager:trust:approve",
    "Approve DNSForge agent enrollments and certificate rotations",
)

MANAGER_ADMIN_ROLE = ManagerRole(
    name="admin",
    permissions=(
        NODE_READER,
        NODE_OPERATOR,
        SYNC_READER,
        SYNC_OPERATOR,
        SYNC_ADMIN,
        BEAT_READER,
        RBAC_ADMIN,
        TRUST_READER,
        TRUST_WRITER,
        TRUST_ADMIN,
        AUDIT_READER,
        INVENTORY_READER,
        INVENTORY_WRITER,
        COMPLIANCE_READER,
        COMPLIANCE_OPERATOR,
        TRUST_APPROVER,
    ),
)

MANAGER_OPERATOR_ROLE = ManagerRole(
    name="operator",
    permissions=(
        NODE_READER,
        NODE_OPERATOR,
        SYNC_READER,
        SYNC_OPERATOR,
        BEAT_READER,
        TRUST_READER,
        INVENTORY_READER,
        INVENTORY_WRITER,
        COMPLIANCE_READER,
        COMPLIANCE_OPERATOR,
    ),
)

MANAGER_APPROVER_ROLE = ManagerRole(
    name="approver",
    permissions=(
        NODE_READER,
        SYNC_READER,
        SYNC_ADMIN,
        BEAT_READER,
        TRUST_READER,
        TRUST_APPROVER,
        AUDIT_READER,
        INVENTORY_READER,
        COMPLIANCE_READER,
    ),
)

MANAGER_AUDITOR_ROLE = ManagerRole(
    name="auditor",
    permissions=(
        NODE_READER,
        SYNC_READER,
        BEAT_READER,
        TRUST_READER,
        AUDIT_READER,
        INVENTORY_READER,
        COMPLIANCE_READER,
    ),
)

MANAGER_VIEWER_ROLE = ManagerRole(
    name="viewer",
    permissions=(
        NODE_READER,
        SYNC_READER,
        BEAT_READER,
        AUDIT_READER,
        TRUST_READER,
        INVENTORY_READER,
        COMPLIANCE_READER,
    ),
)

MANAGER_ROLES = (
    MANAGER_ADMIN_ROLE,
    MANAGER_OPERATOR_ROLE,
    MANAGER_APPROVER_ROLE,
    MANAGER_AUDITOR_ROLE,
    MANAGER_VIEWER_ROLE,
)
