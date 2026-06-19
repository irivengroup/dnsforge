# DNSForge Operational Runbooks

## Create zone

1. Run `dnsforge readiness`.
2. Run `dnsforge zone create <zone>`.
3. Run `dnsforge zone status <zone>`.
4. Run `dnsforge validate`.
5. Run `dnsforge doctor`.
6. Run `dnsforge cluster audit` when clustered.

## Modify zone

1. Create a backup with `dnsforge zone backup <zone> --reason "planned change"`.
2. Edit with `dnsforge zone edit <zone>`.
3. Validate with `dnsforge validate`.
4. Review `dnsforge zone diff --zone <zone> --from <old> --to <new>`.

## Delete zone

1. Confirm business approval.
2. Run `dnsforge zone backup <zone> --reason "pre-delete"`.
3. Run `dnsforge zone delete <zone>`.
4. Run `dnsforge catalog repair` if catalog zones are enabled.
5. Run `dnsforge validate`.

## Rollback zone

1. Identify target version with `dnsforge zone history <zone>`.
2. Inspect with `dnsforge zone show --zone <zone> --version <id>`.
3. Roll back with `dnsforge zone rollback --zone <zone> --version <id> --reason "rollback"`.
4. Run `dnsforge validate` and `dnsforge doctor`.

## DNSSEC rotation

1. Run `dnsforge dnssec check-expiry`.
2. Run `dnsforge dnssec rotate-zsk` or `dnsforge dnssec rotate-ksk`.
3. Run `dnsforge dnssec validate`.
4. Run `dnsforge validate`.

## Cluster recovery

1. Run `dnsforge cluster audit --format json`.
2. Identify drift.
3. Run `dnsforge cluster sync` only after validation.
4. Re-run `dnsforge cluster audit`.

## Disaster recovery

1. Run `dnsforge disaster snapshot` before risky operations.
2. In incident mode, run `dnsforge disaster verify`.
3. Restore with `dnsforge disaster restore`.
4. Run `dnsforge validate`, `dnsforge doctor`, and `named-checkconf`.

## Upgrade

1. Run `dnsforge readiness`.
2. Run `dnsforge disaster snapshot`.
3. Install the new wheel.
4. Run `dnsforge version`.
5. Run `dnsforge validate`, `dnsforge doctor`, and `dnsforge readiness`.

## Migration

Only proxy migrations are supported:

- `proxy-forwarder -> proxy-hybrid`
- `proxy-hybrid -> proxy-forwarder`

Always use `dnsforge migrate --to <target> --reason "..."`; the migration workflow performs snapshot, render, deploy and rollback handling.


## Operational Readiness JSON

Use `dnsforge readiness --json` for CI, DNSForge Manager, DNSBeat and external supervision. The JSON contract exposes `status`, `score`, and `checks`.
