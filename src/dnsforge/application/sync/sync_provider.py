from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SyncResult:
    provider: str
    status: str
    message: str


class SyncProvider(Protocol):
    name: str

    def sync(self, *, dry_run: bool = False) -> SyncResult:
        raise NotImplementedError


class ClusterSyncProvider:
    name = "cluster"

    def sync(self, *, dry_run: bool = False) -> SyncResult:
        return SyncResult(self.name, "dry-run" if dry_run else "ready", "Cluster sync provider boundary ready")


class FutureDnsSyncProvider:
    name = "dnssync"

    def sync(self, *, dry_run: bool = False) -> SyncResult:
        return SyncResult(self.name, "planned", "Future DNSSync provider boundary reserved")
