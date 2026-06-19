# DNSForge Enterprise CI Validation

DNSForge v12.7.0 extends the quality pipeline from Python/package validation to enterprise DNS operation validation.

## Validation families

The CI must keep the following families active:

1. Python quality gates: Ruff format, Ruff lint, MyPy, Bandit, pip-audit.
2. Product gates: CLI/API/Event/Service coverage, product gate, release gate, clean release gate.
3. Coverage gate: global measured coverage must stay at or above 90%.
4. Real BIND validation: generated BIND configuration must be checked with `named-checkconf` and generated zones with `named-checkzone`.
5. Live BIND smoke validation: where the `named` binary is available, CI starts BIND in foreground under timeout and treats a clean startup window as success.
6. Manager-to-Agent workflow validation: Manager must route changes through DNSSync and DNSForge Agent clients only.
7. Disaster Recovery validation: snapshot, restore and verify paths must be tested end-to-end at service level.
8. Catalog Zones validation: sync and repair must be tested against generated catalog state.
9. DNSSEC lifecycle validation: enable, sign, ZSK/KSK rotation and expiry checks must remain covered.
10. Manager security validation: RBAC, trust approval, token rotation/revocation, replay resistance and read-only DNSBeat behavior must remain covered.

## Non-negotiable product boundary

DNSForge Manager never edits BIND files directly. The only allowed mutation path is:

```text
Manager -> DNSSync -> DNSForge Agent API -> DNSForge local services -> BIND
```

DNSForge Agent remains the only component allowed to write BIND configuration, write zone files, run `rndc`, run `named-checkconf`, run `named-checkzone`, or deploy/rollback local DNS configuration.

## Tooling

`tools/check_enterprise_validation.py` verifies that the repository contains the expected enterprise validation hooks, CI commands and test modules. It is intentionally deterministic and does not require BIND at import time.
