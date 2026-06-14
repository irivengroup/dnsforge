# DNSForge CI quality report

The GitHub Actions pipeline is a blocking Enterprise gate.

The main validation job runs on Python 3.9, 3.11, and 3.13 and enforces:

- Ruff lint
- Ruff format
- mypy
- architecture gates
- pytest
- zero skipped tests in CI
- coverage threshold
- generated BIND configuration validation
- package build
- wheel installation
- `dnsforge --help`
- `dnsforge version`
- artifact upload

Local development may skip BIND validation tests when `named-checkconf` or
`named-checkzone` are absent. CI installs these tools and sets
`DNSFORGE_FORBID_SKIPS=1`, making every skip a failure.
