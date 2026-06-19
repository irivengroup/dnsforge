# DNSForge CI Certification Policy

DNSForge v12.8.0 hardens CI around a minimum supported platform matrix.

## Minimum platform matrix

```text
RHEL / Rocky / Alma 8+
Ubuntu 22.04 LTS+
Debian 10+
SUSE / SLES 12+
```

## CI expectations

The CI must not imply that DNSForge is only supported on the newest GitHub-hosted image. When native runners are unavailable, platform support is enforced through:

1. layout-aware BIND rendering tests;
2. platform support documentation gates;
3. enterprise validation gates;
4. real BIND validation on the available runner;
5. packaging and release hygiene checks.

Dedicated enterprise runners or containers can be added later for each minimum platform family without changing the product support contract.

## Blocking policy

A release must fail if the platform support policy is removed, weakened, or changed away from the approved minimums without an explicit architecture decision.
