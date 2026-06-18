# DNSSync Boundary Preparation

DNSForge v11.0.0 isolates authoritative synchronization logic behind a dedicated sync bounded context:

```text
src/dnsforge/domain/sync/
src/dnsforge/application/sync/
src/dnsforge/infrastructure/sync/
```

The public CLI remains stable:

```bash
dnsforge cluster diff
dnsforge cluster peers
dnsforge cluster sync --dry-run --reason "<motif>"
dnsforge cluster sync --reason "<motif>"
```

`cluster` validates and orchestrates the authoritative HA context. `sync` owns the future-extractable implementation: manifests, checksums, SOA serial inventory, drift detection and peer state reading.
