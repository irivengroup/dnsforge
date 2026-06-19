# DNSForge Manager Security

DNSForge Manager orchestrates DNSForge agents. It never modifies BIND files directly.

## Agent trust model

A node registration creates a pending trust relationship:

1. Manager receives node metadata and DNSForge API endpoint.
2. Manager generates an agent token.
3. Manager computes/stores an agent fingerprint.
4. Node remains `pending` until explicit approval.
5. Only approved nodes can receive DNSSync apply or rollback operations.

Supported trust operations:

- approve node
- revoke node
- rotate agent token

Revoked nodes are disabled and cannot receive operations.

## RBAC

Roles:

- `admin`: full Manager, trust, sync, RBAC and audit access.
- `operator`: node operations and DNSSync orchestration, no trust administration.
- `viewer`: read-only nodes, DNSBeat and audit visibility.

## DNSSync safety

DNSSync requires a dry-run plan hash before apply or rollback. The plan hash binds:

- cluster id
- operation
- payload
- target node ids

This prevents applying a different operation than the one reviewed during dry-run.

## DNSBeat safety

DNSBeat is read-only. It collects health data and must never trigger BIND configuration changes.

## Audit

Manager records security-sensitive operations:

- node registration
- node approval
- node revocation
- agent token rotation
- node status changes

Each audit event stores actor, action, target, timestamp and result.
