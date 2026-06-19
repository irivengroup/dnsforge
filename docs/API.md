# DNSForge Internal API

DNSForge v11.2.0 introduces stable internal Python facades under `dnsforge.api` so the CLI, future REST adapters and DNSForge Manager can use the same application services.

## Facade

```python
from dnsforge.api import DnsForgeApplicationApi
from dnsforge.infrastructure.filesystem.paths import ProjectPaths

api = DnsForgeApplicationApi(ProjectPaths())
```

## Available APIs

- `ZoneApi`: `create_zone`, `update_zone`, `delete_zone`, `enable_zone`, `disable_zone`, `rollback_zone`, `list_zones`, `search_zones`.
- `DnssecApi`: `enable`, `disable`, `rotate_ksk`, `rotate_zsk`, `status`.
- `CatalogApi`: `sync`, `repair`, `validate`, `status`.
- `ClusterApi`: `audit_cluster`, `sync`, `validate`, `status`.
- `DisasterRecoveryApi`: `snapshot`, `restore`, `verify`.

## Events and audit

Critical API operations publish `AuditEvent` objects through `EventBus`. When created through `DnsForgeApplicationApi`, events are also persisted in:

```text
/etc/dnsforge/audit-events.jsonl
```

The repository is append-only JSONL and is intentionally simple so DNSForge Manager, DNSBeat and DNSSync can consume the same event stream later.


## CLI/API parity

The API is an additional integration surface. The local `dnsforge` CLI remains mandatory on every installed server and must keep using shared application services directly. No DNSForge feature may become API-only or GUI-only. See `docs/CLI_API_PARITY.md`.
