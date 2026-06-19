# DNSForge Product Boundaries

DNSForge v12 introduces DNSForge Manager as a separate central management plane. It does not replace DNSForge.

## DNSForge

DNSForge is the local BIND administration agent installed on every managed DNS server.

Responsibilities:

- install and validate BIND prerequisites;
- render local BIND configuration;
- deploy `named.conf`, includes and zone files;
- run BIND validation commands such as `named-checkconf` and `named-checkzone`;
- use `rndc` locally;
- perform local rollback, migration and disaster recovery.

Only DNSForge may modify BIND files or execute local BIND control operations.

## DNSForge Manager

DNSForge Manager is the central management plane for one or more DNSForge nodes.

Responsibilities:

- inventory of DNSForge nodes;
- node registration;
- RBAC foundation;
- central workflows;
- global reporting and audit readiness;
- orchestration through the DNSForge agent API.

DNSForge Manager may be deployed on a server where BIND is not installed. It never edits BIND files directly and never replaces the local DNSForge CLI.

## DNSBeat

DNSBeat is a DNSForge Manager sub-module.

Responsibilities:

- monitoring managed DNSForge nodes;
- collecting health, metrics and readiness signals;
- preparing alerting integration.

DNSBeat is read-oriented and does not modify BIND configuration.

## DNSSync

DNSSync is a DNSForge Manager sub-module.

Responsibilities:

- synchronizing changes initiated through DNSForge Manager;
- orchestrating cluster/site propagation;
- submitting operations to DNSForge agents on managed nodes.

DNSSync orchestrates. DNSForge executes locally. BIND is modified only by DNSForge.

## Canonical write path

```text
Admin
  -> DNSForge Manager
  -> DNSSync
  -> DNSForge API on each target node
  -> DNSForge local execution
  -> BIND
```

Forbidden path:

```text
DNSForge Manager -> SSH/filesystem -> BIND files
```

## CLI rule

Every DNSForge server remains locally administrable with the DNSForge CLI. All DNSForge CLI commands require elevated privileges except:

```bash
dnsforge version
```
