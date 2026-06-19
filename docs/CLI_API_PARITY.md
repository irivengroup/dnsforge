# DNSForge CLI/API Parity Contract

DNSForge keeps the local `dnsforge` command as a primary administration interface on every installed server.

The API layer introduced for DNSForge Manager, REST adapters, DNSBeat and DNSSync is an additional integration surface. It must not replace the local CLI and must not make the node dependent on a remote manager or HTTP endpoint.

## Non-negotiable rules

1. Every installed DNSForge node must remain locally administrable with `dnsforge ...`.
2. No operational feature may exist only in the API, REST layer or GUI.
3. CLI and API entry points must call shared application services.
4. The CLI must not import `dnsforge.api` to execute local operations.
5. DNSForge Manager is optional. Loss of Manager/API connectivity must not block local operations.

## Required local CLI domains

The following command domains are protected by release tests and must remain available:

- `dnsforge acl`
- `dnsforge audit`
- `dnsforge backup`
- `dnsforge catalog`
- `dnsforge cluster`
- `dnsforge config`
- `dnsforge deploy`
- `dnsforge disaster`
- `dnsforge dnssec`
- `dnsforge doctor`
- `dnsforge generate`
- `dnsforge health`
- `dnsforge initialize`
- `dnsforge migrate`
- `dnsforge profile`
- `dnsforge render`
- `dnsforge restore`
- `dnsforge rpz`
- `dnsforge security`
- `dnsforge status`
- `dnsforge validate`
- `dnsforge version`
- `dnsforge view`
- `dnsforge zone`

## Target architecture

```text
CLI DNSForge          API/REST/Manager
     │                      │
     └──────────┬───────────┘
                ▼
        Application Services
                ▼
              Domain
                ▼
          Infrastructure
```

Forbidden architecture:

```text
CLI DNSForge -> HTTP API -> Application Services
```

The CLI must work without HTTP, PostgreSQL, DNSForge Manager, DNSBeat or DNSSync.
