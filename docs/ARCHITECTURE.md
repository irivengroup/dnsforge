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
