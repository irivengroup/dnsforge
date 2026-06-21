# DNSForge Manager Agent API Control Plane

DNSForge Manager does not modify BIND files locally. It resolves trusted agents from Inventory, verifies RBAC, then submits commands to the DNSForge Agent API.

## Guarantees

- request-scoped `request_id`;
- idempotency key;
- normalized execution result;
- cluster fan-out through bounded workers sized from server characteristics;
- JSON backend remains the default;
- PostgreSQL remains optional.

## CLI

```bash
dnsforge-manager agent execute --node-id ns01 --action status --operation status
dnsforge-manager agent execute-cluster --cluster-id authoritative-a --action zone --operation zone.list
```

## API

```text
POST /agents/{node_id}/execute
POST /agents/clusters/{cluster_id}/execute
```
