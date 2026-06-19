# DNSForge Manager Persistence

DNSForge Manager uses explicit repository boundaries for all stateful Manager data.

## Responsibilities

- Inventory and node lifecycle are persisted through `NodeInventoryRepository`.
- Change requests are persisted through `ChangeRequestRepository`.
- Manager audit events are persisted through `ManagerAuditRepository`.
- JSON remains the default backend.
- PostgreSQL is prepared behind a typed backend boundary and versioned schema migrations.

## Default backend: JSON

The JSON backend is dependency-free and suitable for single Manager deployments and development.
All writes are atomic and change request mutations are protected by a local lock file.

## PostgreSQL readiness

PostgreSQL is represented by:

- `ManagerPersistenceConfig`
- `PersistenceBackend.POSTGRESQL`
- `PostgreSQLPersistenceBackend`
- `MANAGER_SCHEMA_MIGRATIONS`

The v12.6.0 release intentionally does not require PostgreSQL at runtime. The Manager can still run without any BIND installation and without a database server.

## Boundary rule

Persistence never changes the DNS responsibility boundary:

```text
Manager orchestrates.
DNSSync synchronizes.
DNSForge Agent applies locally.
BIND is never modified directly by Manager.
```
