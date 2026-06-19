# DNSForge Go-Live Checklist

## Platform

- [ ] OS is certified: RHEL / Rocky / Alma 8+, Ubuntu 22.04+, Debian 10+, or SUSE / SLES 12+.
- [ ] Python version is supported.
- [ ] BIND packages are installed.
- [ ] `named`, `named-checkconf`, `named-checkzone`, and `rndc` are available.

## DNSForge

- [ ] `/etc/dnsforge/setup.conf` reviewed.
- [ ] `dnsforge readiness` returns READY or accepted WARNING only.
- [ ] `dnsforge initialize --render-only` completed.
- [ ] `dnsforge initialize --apply` completed.
- [ ] `dnsforge validate` passed.
- [ ] `dnsforge doctor` passed.

## DNS controls

- [ ] RNDC configured and validated.
- [ ] TSIG secrets validated.
- [ ] ACL configured.
- [ ] Views configured.
- [ ] DNSSEC baseline validated where applicable.
- [ ] Catalog Zones validated where applicable.

## Resilience

- [ ] Backup tested.
- [ ] Restore tested.
- [ ] Rollback tested.
- [ ] Disaster snapshot tested.
- [ ] Disaster restore tested.
- [ ] Cluster audit passed.

## Manager

- [ ] DNSForge Manager inventory contains expected nodes.
- [ ] DNSBeat health checks are green.
- [ ] DNSSync dry-run reviewed.
- [ ] RBAC roles validated.
