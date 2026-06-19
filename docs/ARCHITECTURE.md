# DNSForge Architecture

DNSForge follows a layered architecture:

```text
CLI / future REST / DNSForge Manager
  -> dnsforge.api facades
  -> application services
  -> domain model
  -> infrastructure adapters
```

The CLI remains backward compatible. Starting with v11.2.0, new integrations should use `dnsforge.api` instead of parsing CLI output.

## Event flow

```text
Application service action
  -> AuditEvent
  -> EventBus
  -> AuditEventRepository(JSONL)
```

This prepares the product boundary for DNSForge Manager, DNSBeat and DNSSync without coupling the DNS engine to a web framework.


## Local CLI remains mandatory

DNSForge Manager and REST adapters are optional entry points. The installed `dnsforge` command remains available on every node and must not depend on HTTP APIs or Manager availability. CLI and API entry points share application services; neither wraps the other for core local operations.

## Enterprise Operations Foundation

DNSForge keeps the CLI as the mandatory local administration interface on every server. Enterprise operations features introduced in v11.3.0 are application services consumed by the CLI and reusable by future API/GUI adapters:

- `JobService` for local operation job definitions and run history.
- `HealthScoreService` for NOC-friendly scoring.
- `ReportService` for unified operational reports.
- `DriftService` for rendered-state drift detection.
- `EventTailService` over the JSONL audit event repository.
- `MetricsCollector` for DNSBeat preparation.
- `SyncProviderService` in `dnsforge.application.sync` for ClusterSync and future DNSSync boundaries.

No feature is API-only or GUI-only; the CLI remains operational without Manager, REST, database, or network connectivity.
