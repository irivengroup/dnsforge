# DNSForge Manager Operational Workflows

DNSForge Manager orchestrates changes through DNSSync and DNSForge agents. It never edits BIND files directly.

## Change request lifecycle

Supported statuses:

- `draft`
- `pending`
- `approved`
- `rejected`
- `applied`
- `failed`
- `rolled_back`

## Mandatory execution path

```text
Manager change request
  -> DNSSync dry-run
  -> admin approval
  -> DNSBeat health gate
  -> DNSSync apply
  -> DNSForge agent local execution
  -> BIND local configuration
```

## API endpoints

- `GET /changes`
- `POST /changes`
- `GET /changes/{change_id}`
- `POST /changes/{change_id}/dry-run`
- `POST /changes/{change_id}/approve`
- `POST /changes/{change_id}/reject`
- `POST /changes/{change_id}/apply`
- `POST /changes/{change_id}/rollback`

## RBAC

- `viewer`: read-only access to changes.
- `operator`: create and dry-run changes.
- `admin`: approve, reject, apply and rollback changes.

## Safety gates

- DNSSync apply and rollback require an approved dry-run plan hash.
- DNSBeat blocks apply if any target node is not clean/healthy.
- DNSForge remains the only component that modifies local BIND configuration.
