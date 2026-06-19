# DNSForge 13.0.x Maintenance Policy

DNSForge 13.0.x is the Production GA maintenance line.

## Scope

Allowed changes:

- Critical bug fixes.
- Security fixes.
- Packaging and release hygiene fixes.
- Documentation corrections.
- CI fixes that preserve the existing product behavior.

Not allowed changes:

- New DNS features.
- Breaking CLI changes.
- Breaking API changes.
- Manager workflow expansion.
- Changes that alter the local DNSForge Agent responsibility boundary.

## Compatibility Rules

- All DNSForge CLI commands remain available locally on each installed server.
- All CLI commands require elevated privileges except `dnsforge version`.
- DNSForge Manager orchestrates through DNSForge Agents and never modifies BIND directly.
- DNSBeat and DNSSync remain Manager submodules.

## Release Requirements

Every 13.0.x release must pass:

- Ruff format and lint.
- MyPy.
- Bandit.
- Product Gate 100/100.
- GA Readiness Gate.
- Release Gate.
- Clean Release Gate.
- Wheel install smoke test.
- Coverage gate when full CI runtime is available.
