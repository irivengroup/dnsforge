from __future__ import annotations

from dnsforge_manager.domain.rbac.models import MANAGER_ROLES, ManagerRole


class RbacService:
    def __init__(self, roles: tuple[ManagerRole, ...] = MANAGER_ROLES) -> None:
        self.roles = {role.name: role for role in roles}

    def role(self, name: str) -> ManagerRole:
        try:
            return self.roles[name]
        except KeyError as exc:
            raise PermissionError(f"unknown Manager role: {name}") from exc

    def require(self, role_name: str, permission_name: str) -> None:
        role = self.role(role_name)
        if not role.allows(permission_name):
            raise PermissionError(f"role {role_name!r} does not allow {permission_name!r}")
