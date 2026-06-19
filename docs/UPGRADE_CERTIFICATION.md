# DNSForge Upgrade Certification

DNSForge v12.9.0 certifies upgrade expectations for enterprise deployments without adding new DNS features.

## Supported platform baseline

Upgrade certification inherits the v12.8.0 minimum platform policy:

- RHEL / Rocky / Alma 8+
- Ubuntu 22.04+
- Debian 10+
- SUSE / SLES 12+

## Certified upgrade paths

- `11.x -> 12.x`
- `12.0.x -> 12.9.x`
- `12.x -> 12.9.x` patch/minor upgrades through wheel or sdist packaging

## Required pre-upgrade safeguards

Before applying an upgrade, operators must preserve:

- `/etc/dnsforge/setup.conf`
- the hidden initialize lock state
- BIND configuration and BIND data
- disaster snapshot metadata
- generated command documentation compatibility

A disaster snapshot is the required pre-upgrade safety anchor for production systems. The certification gate therefore treats disaster snapshot and restore coverage as upgrade-critical.

## Packaging validation

The release process must continue to validate:

- wheel build
- sdist build
- wheel install
- wheel uninstall or isolated virtualenv disposal
- `dnsforge version`
- root-only CLI behavior for every command except `dnsforge version`

## Release gate expectations

The CI gate must include:

```bash
PYTHONPATH=src python tools/check_upgrade_certification.py
PYTHONPATH=src python tools/check_platform_support.py
PYTHONPATH=src python tools/check_enterprise_validation.py
```

A release is not upgrade-certified unless all gates pass together with Ruff, MyPy, Bandit, pytest, coverage, product gate, release gate and clean release checks.
