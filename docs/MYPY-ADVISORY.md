# Mypy advisory gate

DNSForge runs `mypy src/dnsforge` in GitHub Actions as an advisory gate.

The check is intentionally non-blocking in v10.5.25 because the project still contains
legacy service boundaries that need gradual typing cleanup. The CI still surfaces all
type errors early while avoiding regressions in the functional pipeline.

Current policy:

- Python target: 3.9+
- Missing third-party stubs are ignored.
- `no_implicit_optional = true` is enabled.
- Strict untyped definition checks are deferred until the v10.5.26 typing cleanup.

Target path:

1. v10.5.25: advisory mypy gate.
2. v10.5.26: fix high-signal type issues in application/domain/infrastructure contracts.
3. later: make mypy blocking once the error budget reaches zero.


## v10.5.26 targeted cleanup

- Added postponed annotation evaluation consistently across DNSForge modules for Python 3.9 compatibility.
- Added explicit return annotations on active CLI, zone, history and security service methods that were still untyped.
- Kept mypy advisory while preparing the next blocking gate.
