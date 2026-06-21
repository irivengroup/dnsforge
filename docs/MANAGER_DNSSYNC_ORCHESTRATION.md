# DNSForge Manager DNSSync Orchestration

DNSForge Manager is a DNS control plane. It never edits BIND files directly. Synchronization is routed through DNSSync and DNSForge agents.

## Commands

```bash
dnsforge-manager dnssync plans
dnsforge-manager dnssync plan --cluster-id <cluster> --operation <operation> --payload '{}'
dnsforge-manager dnssync validate --plan-hash <hash>
dnsforge-manager dnssync dry-run --cluster-id <cluster> --operation <operation> --payload '{}'
dnsforge-manager dnssync apply --cluster-id <cluster> --operation <operation> --payload '{}' --approved-plan-hash <hash>
dnsforge-manager dnssync rollback --cluster-id <cluster> --operation <operation> --payload '{}' --approved-plan-hash <hash>
dnsforge-manager dnssync status
dnsforge-manager dnssync history [--cluster-id <cluster>]
```

## API

```http
GET  /dnssync/plans
POST /dnssync/plans
POST /dnssync/validate
POST /dnssync/dry-run
POST /dnssync/apply
POST /dnssync/rollback
GET  /dnssync/status
GET  /dnssync/history
```

## Safety model

- Apply and rollback require an approved dry-run plan hash.
- Targets must be registered, approved and not disabled or unreachable.
- The Manager submits operations to DNSForge agents only.
- BIND configuration writes remain local to the DNSForge agent.

## v15.1.0 completion

DNSSync orchestration history is now exposed through the Manager CLI/API and backed by a repository abstraction. Plans, dry-runs, applies and rollbacks remain agent-API operations; the Manager stores orchestration intent and execution results only.
