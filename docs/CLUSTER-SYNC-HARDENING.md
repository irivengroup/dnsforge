# Cluster Sync Hardening

DNSForge authoritative cluster sync now produces a local sync manifest containing:

- local node name;
- target peer count;
- enabled zone count;
- SHA-256 checksum per synchronized file;
- aggregate zone checksum;
- SOA serial checksum;
- manifest SHA-256;
- DNSSEC alignment marker.

`CLUSTER_PEERS` remains supported for HA inventory. If it is not set, DNSForge uses `PEER_AUTHORITATIVE_ADDRESSES` as the authoritative peer list.

Proxy profiles are rejected by cluster validation. Cluster sync remains authoritative-only.
