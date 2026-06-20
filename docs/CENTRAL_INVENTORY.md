# DNSForge Manager Central Inventory

DNSForge v14.2.0 introduces Central Inventory in the Manager. The Manager is the centralized source of truth for sites, clusters, agents, environments and aggregated agent readiness.

## Aggregates

- `Site`: logical or physical DNS operating location.
- `Cluster`: group of DNSForge agents attached to a site and environment.
- `Agent`: registered local DNSForge agent metadata.
- `Environment`: production, staging or any operator-defined runtime boundary.
- `AgentStatus`: readiness state reported or aggregated for an agent.

## Persistence

JSON remains the default backend. PostgreSQL is optional and uses the following tables:

- `sites`
- `clusters`
- `agents`
- `environments`
- `agent_status`

## API

- `GET /inventory/sites`
- `POST /inventory/sites`
- `GET /inventory/clusters`
- `POST /inventory/clusters`
- `GET /inventory/agents`
- `POST /inventory/agents`
- `GET /inventory/environments`

## CLI

```bash
dnsforge-manager inventory site list
dnsforge-manager inventory site create --site-id paris --name "Paris DC"
dnsforge-manager inventory cluster list
dnsforge-manager inventory cluster create --cluster-id auth-a --name "Authoritative A" --site paris
dnsforge-manager inventory agent list
dnsforge-manager inventory agent register --fingerprint fp-001 --hostname dns01 --version 14.2.0 --profile authoritative --site paris --cluster auth-a --status READY
dnsforge-manager inventory environment list
```
## Compliance aggregation

Central Inventory also stores agent Configuration Compliance states.

```bash
dnsforge-manager inventory compliance list
dnsforge-manager inventory compliance update --fingerprint agent-001 --compliance COMPLIANT
dnsforge-manager inventory compliance history [--fingerprint agent-001]
```

API endpoints:

```http
GET  /inventory/agent-compliance
POST /inventory/agent-compliance
```


## Compliance trend summaries

```bash
dnsforge-manager inventory compliance trends
dnsforge-manager inventory compliance trends --fingerprint agent-001
```

API:

```text
GET /inventory/agent-compliance/trends
GET /inventory/agent-compliance/trends?fingerprint=agent-001
GET /inventory/agent-compliance/report
GET /inventory/agent-compliance/report?fingerprint=agent-001
```

The trend summary reports observations, transitions, recurrent drift, first observation, last observation and last transition for each agent.
