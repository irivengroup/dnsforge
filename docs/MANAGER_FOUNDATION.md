# DNSForge Manager Foundation

DNSForge Manager v12.0.0 is a foundation release. It establishes package structure, contracts and safe boundaries without changing the DNSForge local engine.

## Structure

```text
src/dnsforge_manager/
├── api/          # framework-neutral application core
├── core/         # product boundaries
├── dnsbeat/      # Manager monitoring sub-module
├── dnssync/      # Manager synchronization/orchestration sub-module
├── inventory/    # managed DNSForge node inventory
├── rbac/         # role and permission contracts
└── workflows/    # central workflows executed through DNSForge agents
```

## Non-goals of v12.0.0

- no direct BIND file management from Manager;
- no replacement of the DNSForge CLI;
- no mandatory BIND installation on the Manager host;
- no DNSForge local agent behavior change.
