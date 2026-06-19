# DNSForge CLI Compatibility Contract

DNSForge 11.x keeps the local CLI as the primary administration interface on every installed server.

## Compatibility guarantee

- DNSForge 11.x releases are backward compatible for documented commands.
- A documented command may gain optional flags, but existing required arguments and behaviours must remain stable.
- Breaking command changes are reserved for DNSForge 12.x and must be documented in the changelog.

## Local administration guarantee

Every DNSForge server remains fully administrable locally through `dnsforge` even when DNSForge Manager, REST APIs, monitoring, or synchronization products are unavailable.

## Privilege model

All DNSForge CLI commands require elevated privileges for security reasons.

The only exception is:

```bash
dnsforge version
```

Build and CI tooling that needs parser metadata must use scripts under `tools/` instead of bypassing the CLI privilege model.

## Output contract

Commands that expose JSON output must use the DNSForge output envelope:

```json
{
  "status": "success",
  "timestamp": "2026-06-19T10:00:00+00:00",
  "data": {}
}
```
