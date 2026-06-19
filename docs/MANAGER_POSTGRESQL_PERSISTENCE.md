# DNSForge Manager PostgreSQL Persistence

DNSForge Manager keeps JSON persistence as the default embedded backend.
PostgreSQL is introduced in v14.1.0 as an optional backend for multi-user and
centralized deployments.

## Configuration

```ini
MANAGER_DATABASE_BACKEND=postgresql
MANAGER_DATABASE_HOST=db.example.internal
MANAGER_DATABASE_PORT=5432
MANAGER_DATABASE_NAME=dnsforge_manager
MANAGER_DATABASE_USER=dnsforge_manager
MANAGER_DATABASE_PASSWORD=<secret>
```

A DSN may also be provided to the Manager persistence factory when deployment
automation owns secret resolution.

## Scope

PostgreSQL repositories are provided for:

- node inventory;
- change requests;
- audit events.

The Manager still orchestrates only through DNSForge agents. It never writes BIND
configuration files directly.

## Migrations

Schema migrations are idempotent and versioned in the Manager infrastructure
layer. Initial migrations create:

1. `manager_nodes`;
2. `manager_change_requests`;
3. `manager_audit_events`.

## Runtime Policy

- JSON remains the default backend.
- PostgreSQL is opt-in.
- PostgreSQL adapters are driver-injected to avoid forcing a database driver on
  agent-only installations.
