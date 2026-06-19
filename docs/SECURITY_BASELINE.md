# DNSForge Security Baseline

## Principle

DNSForge is the only component allowed to modify local BIND configuration and data. DNSForge Manager, DNSBeat and DNSSync orchestrate or observe through DNSForge and never edit BIND files directly.

## Privileges

All DNSForge commands require root/sudo except `dnsforge version`.

## SELinux and AppArmor

- Validate host confinement before production go-live.
- Ensure BIND can read its configuration and zone paths.
- Keep CI smoke-test runtime isolation separate from production profiles.

## Firewall matrix

| Function | Protocol | Port |
| --- | --- | --- |
| DNS | UDP/TCP | 53 |
| RNDC | TCP | 953 |
| DNSForge Agent API | TCP | configurable |
| DNSForge Manager API | TCP | configurable |

## TSIG and RNDC

- Use node-specific secrets.
- Rotate secrets through documented workflows.
- Do not share RNDC secrets across unrelated nodes.

## ACL and Views

- Never leave global recursive access open.
- Keep internal and external views explicit.
- Validate ACL drift with `dnsforge security audit` and `dnsforge validate`.

## DNSSEC

- Monitor key expiry.
- Use DNSForge commands for signing and rotation.
- Keep rollback and disaster snapshots before major DNSSEC operations.

## Manager security

- Viewer is read-only.
- Operator creates controlled change requests.
- Admin approves and applies changes.
- DNSSync apply requires a prior dry-run plan hash.


## Operational Readiness JSON

Use `dnsforge readiness --json` for CI, DNSForge Manager, DNSBeat and external supervision. The JSON contract exposes `status`, `score`, and `checks`.
