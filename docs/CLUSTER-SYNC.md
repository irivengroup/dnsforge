# DNSForge Authoritative Cluster Sync

DNSForge cluster synchronization is restricted to authoritative DNS servers. Proxy nodes are never cluster members.

Commands:

```bash
dnsforge cluster peers
dnsforge cluster diff
dnsforge cluster sync --dry-run --reason "Review authoritative sync"
dnsforge cluster sync --reason "Apply authoritative sync"
```

The sync service uses `CLUSTER_PEERS` from `/etc/dnsforge/setup.conf`, validates that the node is authoritative, builds a sync plan from the local zone catalog, catalog state, and DNSSEC state, and writes an outbound sync manifest. Peer drift is detected from peer manifests under the cluster sync state directory.

`--reason` is mandatory for sync operations.
