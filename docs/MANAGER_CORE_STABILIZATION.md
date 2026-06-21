# DNSForge Manager Core Stabilization

DNSForge Manager is the secure BIND control plane. It does not edit BIND files directly and it does not implement a generic ITSM workflow engine. Manager resolves inventory targets, verifies trust/readiness/compliance, and delegates DNS operations to DNSForge agents through their secured API.

## Canonical inventory roles

- `authoritative`
- `proxy-forwarder`
- `proxy-hybrid`
- `catalog-publisher`
- `catalog-subscriber`
- `hidden-master`
- `stealth-secondary`

These roles describe BIND responsibility in the fleet inventory. They are not RBAC roles.

## RBAC roles

- `viewer`
- `operator`
- `approver`
- `admin`
- `auditor`

The Manager does not expose `manager:changes:*` permissions. Approval is DNS-specific and applies to sensitive BIND operations such as DNSSync apply/rollback, trust approval, DNSSEC changes and compliance repair.

## Next milestone

The next milestone is `v15.0.0 Agent API Control Plane`: a hardened Manager client for DNSForge Agent API calls with authentication, timeouts, retries, idempotency, normalized errors and audit request IDs.
