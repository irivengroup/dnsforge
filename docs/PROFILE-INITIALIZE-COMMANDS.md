# DNSForge profile initialization commands

DNSForge initialization is profile-driven.

## Authoritative profile

```bash
dnsforge authoritative initialize
dnsforge authoritative initialize --render-only
dnsforge authoritative initialize --apply
```

## Proxy profile

Proxy defaults to `hybrid` when `--type` is omitted.

```bash
dnsforge proxy initialize --type hybrid
dnsforge proxy initialize --type forwarder
dnsforge proxy initialize --type hybrid --render-only
dnsforge proxy initialize --type forwarder --render-only
dnsforge proxy initialize --apply
```

Once a profile is applied, the node is locked by the hidden initialization lock.
Any further initialization attempt, including the opposite profile, is rejected.

The DNSForge wheel installs the Python package and `dnsforge` entrypoint. BIND
package bootstrap is performed by the first privileged `initialize` apply path
when BIND is missing, because Python wheels cannot safely run privileged OS
post-install scripts during `pip install`.
