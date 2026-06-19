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


NODE_READER = ManagerPermission("manager:nodes:read", "Read managed DNSForge nodes")
NODE_OPERATOR = ManagerPermission("manager:nodes:operate", "Submit operations to DNSForge nodes")
SYNC_OPERATOR = ManagerPermission("manager:sync:operate", "Orchestrate cluster synchronization through DNSSync")
BEAT_READER = ManagerPermission("manager:dnsbeat:read", "Read DNSBeat monitoring data")

MANAGER_ADMIN_ROLE = ManagerRole(
    name="manager-admin",
    permissions=(NODE_READER, NODE_OPERATOR, SYNC_OPERATOR, BEAT_READER),
)

MANAGER_VIEWER_ROLE = ManagerRole(
    name="manager-viewer",
    permissions=(NODE_READER, BEAT_READER),
)
