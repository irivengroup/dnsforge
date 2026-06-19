# DNSForge Migration Compatibility

DNSForge v12.9.0 certifies migration compatibility for supported proxy profile transitions.

## Supported platform baseline

Migration compatibility follows the same minimum platform matrix:

- RHEL / Rocky / Alma 8+
- Ubuntu 22.04+
- Debian 10+
- SUSE / SLES 12+

## Supported migrations

- `proxy-forwarder -> proxy-hybrid`
- `proxy-hybrid -> proxy-forwarder`

No migration is certified between authoritative and proxy roles.

## Required migration guarantees

Every supported migration must preserve or transactionally manage:

- `/etc/dnsforge/setup.conf`
- BIND configuration
- BIND data
- zone data
- migration snapshot metadata
- rollback metadata

The migration flow remains:

```text
validate current profile
snapshot setup.conf
snapshot BIND configuration
snapshot BIND data
render target profile
deploy
validate
commit
```

If any critical step fails, rollback must restore the previous setup.conf, BIND configuration and BIND data from the snapshot.

## Compatibility contract

The following behavior must remain stable across 12.x:

- only proxy-forwarder/proxy-hybrid migrations are allowed
- migration requires elevated privileges
- migration requires an operator reason
- dry-run never mutates filesystem state
- rollback restores the previous profile state

## CI gate

Migration compatibility is guarded by:

```bash
PYTHONPATH=src python tools/check_upgrade_certification.py
```

and by the existing migration, disaster, release and platform support tests.
