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
