# DNSForge test skip policy

DNSForge CI must not hide incomplete features behind generic skipped tests.

Approved skip contexts are limited to:

- BIND validation tools missing in a local developer environment (`named-checkconf`, `named-checkzone`).
  In GitHub Actions, this is never allowed: the workflow must install BIND tools and tests must fail if they are absent.
- Install script tests running without root privileges.
- Install maintenance script tests running without root privileges.

The CI installs BIND validation tools before running pytest. The main CI job is therefore expected to execute BIND configuration validation without BIND-tool skips.
The CI runs pytest with `-rs` so every skipped test includes its reason in logs.
The architecture test `tests/architecture/test_skip_policy.py` fails on any unapproved skip reason.


## CI BIND tools gate

The generated BIND configuration validation tests are allowed to skip only on local developer workstations where `named-checkconf` or `named-checkzone` are missing.

Under GitHub Actions (`GITHUB_ACTIONS=true`), missing BIND tools are a hard failure. The workflow installs `bind9utils` and `bind9-dnsutils` before pytest, so the main CI job must validate generated BIND configuration without BIND-tool skips.
