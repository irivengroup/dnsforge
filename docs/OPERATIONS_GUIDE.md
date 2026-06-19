# DNSForge Operations Guide

DNSForge is the local BIND administration agent. It installs, renders, validates, deploys and rolls back BIND configuration on the server where it is installed. DNSForge Manager orchestrates one or more DNSForge agents and never edits BIND files directly.

## Production topology

Supported minimum platforms:

- RHEL / Rocky / Alma 8+
- Ubuntu 22.04+
- Debian 10+
- SUSE / SLES 12+

Each DNS server runs DNSForge locally. DNSForge Manager may run on a server without BIND installed.

## Installation and initialization

1. Install DNSForge from the validated wheel or release archive.
2. Review `/etc/dnsforge/setup.conf`.
3. Run `dnsforge readiness` to check operational prerequisites.
4. Run `dnsforge initialize --render-only` to generate and inspect the BIND configuration.
5. Run `dnsforge initialize --apply` when the rendered configuration is validated.
6. Run `dnsforge validate` and `dnsforge doctor` after deployment.

All DNSForge commands require elevated privileges except `dnsforge version`.

## Daily operations

Use DNSForge CLI locally for emergency operations and DNSForge Manager for centralized workflows.

Core local commands:

- `dnsforge readiness`
- `dnsforge status`
- `dnsforge validate`
- `dnsforge doctor`
- `dnsforge zone ...`
- `dnsforge dnssec ...`
- `dnsforge catalog ...`
- `dnsforge cluster ...`
- `dnsforge disaster ...`

## Backup, restore and rollback

Before major changes:

1. Run `dnsforge disaster snapshot`.
2. Validate the snapshot is present.
3. Apply the change.
4. Use `dnsforge zone rollback`, `dnsforge config rollback`, or `dnsforge disaster restore` depending on the failure scope.

## DNSSEC lifecycle

Run DNSSEC operations through DNSForge so that history, validation and rollback metadata remain coherent:

- `dnsforge dnssec enable`
- `dnsforge dnssec sign`
- `dnsforge dnssec rotate-zsk`
- `dnsforge dnssec rotate-ksk`
- `dnsforge dnssec check-expiry`

## Catalog Zones and cluster

For authoritative clusters, validate catalog zone membership before and after changes:

- `dnsforge catalog validate`
- `dnsforge catalog sync`
- `dnsforge catalog repair`
- `dnsforge cluster audit --format json`

## Manager workflows

Manager changes follow the sequence:

`Manager -> DNSSync dry-run -> approval -> DNSSync apply -> DNSForge agent -> BIND`

Manager never edits `named.conf`, zone files, RNDC or BIND runtime files directly.
