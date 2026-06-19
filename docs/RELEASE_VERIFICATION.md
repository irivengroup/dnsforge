# DNSForge 13.0.x Maintenance Release Verification

DNSForge 13.0.x is a maintenance branch. Maintenance releases must not introduce new DNS, Manager, DNSBeat or DNSSync features. They may only correct defects, close CI/release debt, improve release hygiene, or update operational documentation.

## Verification scope

A maintenance release is acceptable only when the following gates remain available and executable:

- Ruff formatting and linting
- MyPy static typing
- Bandit security scan
- Product Gate
- Operational Readiness Gate
- Platform Support Gate
- Upgrade Certification Gate
- GA Readiness Gate
- Release Gate
- Clean Release Gate
- Wheel install smoke test
- Twine artifact validation

## Runtime validation policy

The live BIND smoke suite stays isolated from the coverage gate. It validates generated BIND configuration and runtime startup behavior without making the coverage job dependent on privileged or host-specific BIND execution.

## Release artifact policy

A valid 13.0.x archive must include:

- `dist/*.whl`
- `dist/*.tar.gz`
- `.github/workflows/ci.yml`
- `docs/RELEASE_VERIFICATION.md`
- `docs/MAINTENANCE_POLICY.md`
- GA and operational documentation

It must not include:

- `__pycache__`
- `.pytest_cache`
- `.mypy_cache`
- `.ruff_cache`
- `build/`
- `*.egg-info` outside `dist/`
- compiled Python bytecode outside built distribution artifacts

## 13.0.4 result

DNSForge 13.0.4 is a maintenance verification release. It does not change product behavior. It confirms the maintenance branch packaging, documentation and gates remain coherent after the CI runtime stabilization work introduced in 13.0.3.
