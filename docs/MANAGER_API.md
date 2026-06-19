# DNSForge Manager API

DNSForge Manager v12.2.0 introduces the first Manager API lifecycle contract.

## Scope

Manager orchestrates DNSForge agents. It never edits BIND files, never runs `rndc`, and never requires BIND on the Manager host.

## Foundation endpoints

- `GET /health`
- `GET /version`
- `GET /nodes`
- `POST /nodes`
- `GET /nodes/{node_id}`
- `GET /nodes/{node_id}/status`

## Node lifecycle

Supported node states:

- `registered`
- `active`
- `unreachable`
- `disabled`

Registration returns an agent token to be used by the local DNSForge agent integration.

## DNSSync workflow

All Manager-originated changes follow this chain:

```text
Manager -> DNSSync -> DNSForge local agent -> BIND
```

Supported workflow stages:

- plan
- dry-run
- apply
- rollback

## DNSBeat

DNSBeat is a Manager sub-module. It reports per-node health score, last seen and drift status, without modifying configuration.


## Security lifecycle endpoints

- `POST /nodes/{id}/approve` approves a pending DNSForge agent.
- `POST /nodes/{id}/revoke` revokes and disables an agent.
- `POST /nodes/{id}/rotate-token` rotates the agent token.
- `GET /audit` exposes Manager audit events according to RBAC.
