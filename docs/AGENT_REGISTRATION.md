# DNSForge Agent Registration

Agent registration records the operational identity of each local DNSForge agent managed by DNSForge Manager.

## Required metadata

- `fingerprint`
- `hostname`
- `version`
- `profile`
- `site`
- `cluster`

## Readiness

Each agent exposes one of three readiness states:

- `READY`
- `WARNING`
- `FAILED`

The Manager aggregates readiness by selecting the worst active state across known agent statuses. `FAILED` dominates `WARNING`, and `WARNING` dominates `READY`.
