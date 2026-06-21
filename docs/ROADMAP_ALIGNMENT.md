# DNSForge Manager 14.x Roadmap Alignment

## Decision

The generic Change Management layer is removed from the 14.x branch. DNSForge Manager remains a DNS/BIND control plane and not a generic ITSM or workflow product.

## Current alignment

| Roadmap item | Status | Notes |
| --- | --- | --- |
| 14.1 PostgreSQL Persistence | Implemented | JSON remains default; PostgreSQL remains optional. |
| 14.2 Central Inventory | Implemented, role model still expandable | Sites, clusters, agents, environments, status and compliance are present. |
| 14.3 DNSSync Orchestration | Re-centered in 14.8.4 | API/CLI expose plan, validate, dry-run, apply, rollback and status. |
| 14.4 DNSBeat Monitoring | Partial | Existing DNSBeat/readiness needs deeper BIND/RNDC/DNSSEC/catalog monitoring. |
| 14.5 Enterprise RBAC | Partial | Admin/operator/viewer exist; approver/auditor are still pending. |

## DNSSync control plane

Manager exposes DNS-specific orchestration only:

- `GET /dnssync/plans`
- `POST /dnssync/plans`
- `POST /dnssync/validate`
- `POST /dnssync/dry-run`
- `POST /dnssync/apply`
- `POST /dnssync/rollback`
- `GET /dnssync/status`

CLI parity:

- `dnsforge-manager dnssync plans`
- `dnsforge-manager dnssync plan`
- `dnsforge-manager dnssync validate`
- `dnsforge-manager dnssync dry-run`
- `dnsforge-manager dnssync apply`
- `dnsforge-manager dnssync rollback`
- `dnsforge-manager dnssync status`

## Next priorities

1. Complete DNSBeat Monitoring with BIND, RNDC, DNSSEC, Catalog and Cluster health.
2. Complete Enterprise RBAC with approver and auditor roles.
3. Expand Inventory role taxonomy for hidden master, catalog publisher/subscriber and stealth secondary.
