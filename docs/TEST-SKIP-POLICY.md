# DNSForge test skip policy

DNSForge CI must not hide incomplete features behind generic skipped tests.

Approved skip contexts are limited to:

- BIND validation tools missing in the current environment (`named-checkconf`, `named-checkzone`).
- Install script tests running without root privileges.
- Install maintenance script tests running without root privileges.

The CI runs pytest with `-rs` so every skipped test includes its reason in logs.
The architecture test `tests/architecture/test_skip_policy.py` fails on any unapproved skip reason.
