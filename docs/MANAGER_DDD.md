# DNSForge Manager DDD Architecture

DNSForge Manager follows the same architectural discipline as the DNSForge agent.

## Responsibility boundary

DNSForge Manager is a central management plane. It does not install BIND, it does not edit BIND files, and it does not execute BIND control commands directly. Every configuration change is orchestrated through DNSSync and applied locally by DNSForge agents.

## Layers

```text
src/dnsforge_manager/
├── domain/
│   ├── audit/
│   ├── core/
│   ├── dnsbeat/
│   ├── dnssync/
│   ├── inventory/
│   ├── rbac/
│   ├── security/
│   └── workflows/
├── application/
│   ├── core/
│   ├── dnsbeat/
│   ├── dnssync/
│   ├── inventory/
│   ├── rbac/
│   ├── security/
│   └── workflows/
├── infrastructure/
│   ├── audit/
│   ├── dnssync/
│   └── inventory/
└── interfaces/
    ├── api/
    └── cli/
```

## Domain

The domain layer contains business concepts and invariants only:

- managed nodes;
- node roles and statuses;
- Manager roles and permissions;
- agent trust states;
- DNSBeat health samples;
- DNSSync plans and executions;
- product boundaries.

The domain layer must not depend on FastAPI, filesystems, HTTP clients, JSON repositories, CLIs or BIND.

## Application

The application layer coordinates use cases:

- node registration;
- agent approval, revocation and token rotation;
- Manager RBAC checks;
- DNSBeat health collection;
- DNSSync planning/execution;
- framework-neutral Manager application facade.

## Infrastructure

The infrastructure layer implements technical adapters:

- JSON node inventory repository;
- in-memory inventory repository for tests/local operation;
- Manager audit repository;
- DNSForge node client abstractions.

## Interfaces

The interfaces layer exposes Manager capabilities:

- FastAPI adapter;
- CLI adapter.

The legacy import paths under `dnsforge_manager.api`, `dnsforge_manager.inventory`, `dnsforge_manager.rbac`, `dnsforge_manager.dnsbeat`, `dnsforge_manager.dnssync`, `dnsforge_manager.security`, `dnsforge_manager.audit`, and `dnsforge_manager.workflows` remain compatibility facades to avoid regressions.

## Non-regression rule

The following public behaviours must remain stable:

- `dnsforge-manager version`;
- `dnsforge-manager health`;
- Manager FastAPI routes;
- node registration lifecycle;
- RBAC enforcement;
- DNSSync dry-run hash requirement;
- DNSBeat read-only monitoring;
- product boundary rule: only DNSForge agents modify BIND.
