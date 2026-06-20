# DNSForge v14.8.0 Manager Compliance Aggregation

DNSForge Manager aggregates local agent Configuration Compliance Engine results without editing BIND files.

## Agent payload

Agents report compliance through Central Inventory using the canonical states:

- `COMPLIANT`
- `WARNING`
- `DRIFTED`
- `FAILED`

Example payload:

```json
{
  "fingerprint": "agent-001",
  "compliance": "DRIFTED",
  "drift_count": 2,
  "last_checked": "2026-06-20T14:00:00Z",
  "message": "manual BIND changes detected",
  "findings": [
    {"resource": "/etc/named.conf", "severity": "CRITICAL"}
  ]
}
```

## API

```http
GET  /inventory/agent-compliance
POST /inventory/agent-compliance
```

The Manager returns an aggregate state, all agent states, a per-state summary and the total drift count.

## CLI

```bash
dnsforge-manager inventory compliance list

dnsforge-manager inventory compliance update \
  --fingerprint agent-001 \
  --compliance DRIFTED \
  --drift-count 2 \
  --last-checked 2026-06-20T14:00:00Z \
  --message "manual BIND changes detected"
```

## Design constraints

- DNSForge remains the local BIND agent.
- DNSForge Manager only stores and aggregates reported compliance state.
- No remediation is applied centrally by this feature.
- JSON remains the default backend; PostgreSQL can map the same object model in a later persistence migration.

## Compliance history

DNSForge Manager stores every compliance update as an immutable history event so operators can distinguish the current state from repeated or recent drift transitions.

CLI:

```bash
dnsforge-manager inventory compliance history
dnsforge-manager inventory compliance history --fingerprint agent-001
```

API:

```text
GET /inventory/agent-compliance/history
GET /inventory/agent-compliance/history?fingerprint=agent-001
```

Each event records the current compliance state, previous compliance state, drift count, observation timestamp and whether the update represents a transition.
