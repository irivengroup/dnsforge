# DNSForge Readiness

`dnsforge readiness` provides the first operational acceptance assessment for a local DNSForge agent.

The command checks the minimum supported platform, Python version, BIND tooling, initialization state, backup repository and history repository availability.

The command is local, requires elevated privileges like every DNSForge command except `dnsforge version`, and returns a non-zero exit code when a critical readiness check fails.

Example:

```bash
dnsforge readiness
```

JSON output is available for integration:

```bash
dnsforge readiness --format json
```
