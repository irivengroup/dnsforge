from __future__ import annotations

import json

from dnsforge.application.sync_foundation.sync_provider import ClusterSyncProvider, FutureDnsSyncProvider, SyncProvider


class SyncFoundationService:
    def __init__(self, providers: list[SyncProvider] | None = None) -> None:
        self.providers = providers or [ClusterSyncProvider(), FutureDnsSyncProvider()]

    def providers_status(self) -> str:
        rows = []
        for provider in self.providers:
            result = provider.sync(dry_run=True)
            rows.append({"provider": result.provider, "status": result.status, "message": result.message})
        return json.dumps(rows, indent=2, sort_keys=True)
