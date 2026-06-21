# DNSForge Manager v15.0.0 - Change Management & Orchestration

DNSForge Manager is the central orchestrator for controlled DNS changes. It never edits BIND files directly; every execution is gated and routed through trusted DNSForge agents.

## Workflow

```text
DRAFT -> REVIEWED -> APPROVED -> EXECUTING -> COMPLETED
                                  |              |
                                  v              v
                                FAILED -> ROLLED_BACK
```

## Gates

Execution is allowed only when:

- readiness is `READY`;
- trust is `TRUSTED` or `APPROVED`;
- compliance is `COMPLIANT` or `WARNING`.

`DRIFTED`, `FAILED`, untrusted agents or non-ready agents block execution.

## CLI

```bash
dnsforge-manager change create --title "Create zone" --target-scope CLUSTER --target-id auth-a --operation zone.create --payload '{"zone":"example.com"}'
dnsforge-manager change list
dnsforge-manager change status --change-id <id>
dnsforge-manager change review --change-id <id>
dnsforge-manager change approve --change-id <id> --comment "approved"
dnsforge-manager change execute --change-id <id>
dnsforge-manager change rollback --change-id <id> --reason "post-check failed"
```

## API

```text
POST /changes
GET  /changes
GET  /changes/{change_id}
GET  /changes/{change_id}/status
POST /changes/{change_id}/review
POST /changes/{change_id}/approve
POST /changes/{change_id}/execute
POST /changes/{change_id}/rollback
```

## Domain objects

- `ChangeRequest`
- `ChangePlan`
- `ChangeApproval`
- `ChangeExecution`
- `ChangeRollback`

## Risk levels

- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`
