# DNSForge Performance Baseline

This document defines the GA baseline scenarios used to detect future performance regressions. It is a product contract for release validation; measurements must be refreshed in controlled environments before GA declaration.

## Baseline commands

The following commands are part of the operational performance baseline:

- `dnsforge initialize --render-only`
- `dnsforge initialize --apply`
- `dnsforge validate`
- `dnsforge readiness`
- `dnsforge catalog sync`

## Zone scale scenarios

| Scenario | Zone count | Purpose |
|---|---:|---|
| Small | 100 | Validate standard branch-office deployments. |
| Medium | 500 | Validate enterprise regional deployments. |
| Large | 1000 | Validate central enterprise DNS platforms. |

## Manager scale scenarios

| Scenario | Agent count | Purpose |
|---|---:|---|
| Small | 10 | Basic Manager orchestration validation. |
| Medium | 100 | Enterprise inventory and DNSBeat validation. |
| Large | 500 | DNSSync planning and audit scalability validation. |

## Acceptance rule

A GA candidate must keep the baseline commands stable, deterministic, and free of critical regression against the previous certified release. Any regression must be documented before release approval.
